import os
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
from passlib.context import CryptContext
from dotenv import load_dotenv
import jwt
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re
import html
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
import google.genai as genai

# Load env variables from .env in the same directory
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

# Settings from .env
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "AIzaSyAjPqJAl2QRbG7SHrAQh5IyCAmyXEAr9hQ")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week

# Initialize Supabase
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials not found. Please ensure .env is properly set up.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configure Gemini AI
if GEMINI_API_KEY:
    genai_client = genai.Client(api_key=GEMINI_API_KEY)
else:
    genai_client = None
    print("Warning: GEMINI_API_KEY not set. AI features will not work.")

# Initialize Flask
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "../frontend"), static_url_path="")
app.config['JSON_SORT_KEYS'] = False

# Configure CORS
frontend_origins = os.getenv(
    "FRONTEND_ORIGINS",
    "http://127.0.0.1:5500,http://localhost:5500,http://127.0.0.1:8000,http://localhost:8000,file://"
)
allow_origins = [origin.strip() for origin in frontend_origins.split(",") if origin.strip()]
if not allow_origins:
    allow_origins = ["http://127.0.0.1:5500", "http://localhost:5500", "file://"]

CORS(app, resources={r"/api/*": {"origins": allow_origins}})

# Password & JWT utilities
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependency: Get current user from JWT token
def get_current_user():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except jwt.InvalidTokenError:
        return None
    
    response = supabase.table("users").select("*").eq("username", username).execute()
    if not response.data:
        return None
    
    return response.data[0]

# Decorator to require authentication
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"detail": "Could not validate credentials"}), 401
        return f(user, *args, **kwargs)
    return decorated_function

# Decorator to require admin role
def require_admin(f):
    @wraps(f)
    def decorated_function(user, *args, **kwargs):
        if not user.get("is_admin"):
            return jsonify({"detail": "Not authorized. Admins only."}), 403
        return f(user, *args, **kwargs)
    return decorated_function

# ====================== ENDPOINTS ======================

@app.route('/')
def read_root():
    if request.accept_mimetypes.accept_html >= request.accept_mimetypes.accept_json:
        return app.send_static_file('demo.html')
    return jsonify({"status": "online", "message": "SkillStalker API is running"})

@app.route('/api/auth/register', methods=['POST'])
def register_user():
    data = request.get_json()
    
    if not data or not all(k in data for k in ('fullname', 'username', 'email', 'password')):
        return jsonify({"detail": "Missing required fields"}), 400
    
    # Check if username already exists
    existing_user = supabase.table("users").select("id").eq("username", data['username']).execute()
    if existing_user.data:
        return jsonify({"detail": "Username already registered"}), 400
    
    # Check if email already exists
    existing_email = supabase.table("users").select("id").eq("email", data['email']).execute()
    if existing_email.data:
        return jsonify({"detail": "Email already registered"}), 400
    
    # Determine if admin
    is_admin = (data['username'] == "skillstalkeradmin")
    
    # Create new user
    new_user = {
        "fullname": data['fullname'],
        "username": data['username'],
        "email": data['email'],
        "password_hash": get_password_hash(data['password']),
        "is_admin": is_admin
    }
    
    insert_resp = supabase.table("users").insert(new_user).execute()
    if not insert_resp.data:
        return jsonify({"detail": "Failed to create user"}), 500
    
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/api/auth/login', methods=['POST'])
def login_user():
    data = request.get_json()
    
    if not data or not all(k in data for k in ('username', 'password')):
        return jsonify({"detail": "Missing username or password"}), 400
    
    # Find user by username
    response = supabase.table("users").select("*").eq("username", data['username']).execute()
    
    if not response.data:
        return jsonify({"detail": "Invalid username or password"}), 401
    
    db_user = response.data[0]
    if not verify_password(data['password'], db_user["password_hash"]):
        return jsonify({"detail": "Invalid username or password"}), 401
    
    # Generate token
    access_token = create_access_token(data={"sub": db_user["username"]})
    return jsonify({"access_token": access_token, "token_type": "bearer"}), 200

@app.route('/api/auth/me', methods=['GET'])
@require_auth
def get_me(current_user):
    return jsonify({
        "id": current_user["id"],
        "fullname": current_user["fullname"],
        "username": current_user["username"],
        "email": current_user["email"],
        "is_admin": current_user.get("is_admin", False)
    }), 200

@app.route('/api/auth/change-password', methods=['POST'])
@require_auth
def change_password(current_user):
    data = request.get_json()
    
    if not data or not all(k in data for k in ('username', 'current_password', 'new_password')):
        return jsonify({"detail": "Missing required fields"}), 400
    
    # Check authorization
    if current_user["username"] != data['username'] and not current_user.get("is_admin"):
        return jsonify({"detail": "Not authorized to change this password"}), 403
    
    # Find target user
    user_resp = supabase.table("users").select("*").eq("username", data['username']).execute()
    if not user_resp.data:
        return jsonify({"detail": "User not found"}), 404
    
    db_user = user_resp.data[0]
    
    # Verify current password
    if not verify_password(data['current_password'], db_user["password_hash"]):
        return jsonify({"detail": "Incorrect current password"}), 401
    
    # Update password
    new_hash = get_password_hash(data['new_password'])
    supabase.table("users").update({"password_hash": new_hash}).eq("username", data['username']).execute()
    
    return jsonify({"message": "Password changed successfully"}), 200

@app.route('/api/user/progress', methods=['PUT'])
@require_auth
def save_user_progress(current_user):
    data = request.get_json()
    
    if not data or 'profile_data' not in data:
        return jsonify({"detail": "Missing profile_data"}), 400
    
    # Save progress
    update_resp = supabase.table("users").update({
        "profile_data": data['profile_data']
    }).eq("username", current_user["username"]).execute()
    
    if not update_resp.data:
        return jsonify({"detail": "Failed to save user progress"}), 500
    
    return jsonify({"message": "User progress saved successfully"}), 200

@app.route('/api/user/progress', methods=['GET'])
@require_auth
def get_user_progress(current_user):
    response = supabase.table("users").select("profile_data").eq("username", current_user["username"]).execute()
    
    if not response.data:
        return jsonify({"profile_data": {}}), 200
    
    user_data = response.data[0]
    profile_data = user_data.get("profile_data") or {}
    
    return jsonify({"profile_data": profile_data}), 200

@app.route('/api/users', methods=['GET'])
@require_auth
@require_admin
def get_all_users(current_user):
    response = supabase.table("users").select("id, fullname, username, email, is_admin").order("id").execute()
    return jsonify({"users": response.data}), 200

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@require_auth
@require_admin
def delete_user(current_user, user_id):
    # Prevent deleting self
    if current_user["id"] == user_id:
        return jsonify({"detail": "Cannot delete your own admin account"}), 400
    
    supabase.table("users").delete().eq("id", user_id).execute()
    return jsonify({"message": "User deleted successfully"}), 200

@app.route('/api/admin/test-user', methods=['POST'])
@require_auth
@require_admin
def create_test_user(current_user):
    import random
    test_id = random.randint(1000, 9999)
    test_username = f"student_test_{test_id}"
    
    new_user = {
        "fullname": f"Test Student {test_id}",
        "username": test_username,
        "email": f"test_{test_id}@skillstalker.com",
        "password_hash": get_password_hash("2026"),
        "is_admin": False
    }
    
    supabase.table("users").insert(new_user).execute()
    return jsonify({"message": "Test user generated", "username": test_username}), 201

@app.route('/api/admin/videos', methods=['POST'])
@require_auth
@require_admin
def create_video(current_user):
    data = request.get_json()

    if not data or 'title' not in data or 'url' not in data or 'category' not in data:
        return jsonify({"detail": "title, url, and category are required"}), 400

    new_video = {
        "title": data['title'],
        "description": data.get('description', ''),
        "url": data['url'],
        "category": data['category'],
        "keywords": data.get('keywords', ''),
        "thumbnail_url": data.get('thumbnail_url')
    }

    insert_resp = supabase.table("videos").insert(new_video).execute()
    if not insert_resp.data:
        return jsonify({"detail": "Failed to create video"}), 500

    return jsonify({"message": "Video created successfully", "video": insert_resp.data[0]}), 201

@app.route('/api/admin/videos/<video_id>', methods=['PUT'])
@require_auth
@require_admin
def update_video(current_user, video_id):
    data = request.get_json()
    
    if not data:
        return jsonify({"detail": "No data provided"}), 400
    
    # Update the video
    update_data = {}
    if 'title' in data:
        update_data['title'] = data['title']
    if 'description' in data:
        update_data['description'] = data['description']
    if 'url' in data:
        update_data['url'] = data['url']
    if 'category' in data:
        update_data['category'] = data['category']
    if 'keywords' in data:
        update_data['keywords'] = data['keywords']
    if 'thumbnail_url' in data:
        update_data['thumbnail_url'] = data['thumbnail_url']
    
    if not update_data:
        return jsonify({"detail": "No valid fields to update"}), 400
    
    update_resp = supabase.table("videos").update(update_data).eq("id", video_id).execute()
    
    if not update_resp.data:
        return jsonify({"detail": "Video not found or update failed"}), 404
    
    return jsonify({"message": "Video updated successfully", "video": update_resp.data[0]}), 200

@app.route('/api/admin/videos/<video_id>', methods=['DELETE'])
@require_auth
@require_admin
def delete_video(current_user, video_id):
    delete_resp = supabase.table("videos").delete().eq("id", video_id).execute()
    if not delete_resp.data:
        return jsonify({"detail": "Video not found or delete failed"}), 404
    return jsonify({"message": "Video deleted successfully"}), 200

@app.route('/api/videos/<video_id>', methods=['GET'])
def get_video(video_id):
    response = supabase.table("videos").select("*").eq("id", video_id).execute()
    if not response.data:
        return jsonify({"detail": "Video not found"}), 404
    return jsonify(response.data[0]), 200

# YouTube helper utilities

def parse_iso8601_duration(duration):
    pattern = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")
    match = pattern.match(duration or "")
    if not match:
        return duration or "0:00"

    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def _urlopen_with_browser_headers(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        return response.read().decode("utf-8")


def _parse_yt_initial_player_response(html_text):
    match = re.search(r"ytInitialPlayerResponse\s*=\s*(\{.+?\})\s*;", html_text, re.DOTALL)
    if not match:
        return None

    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def _fetch_caption_tracks_from_watch_page(video_id):
    page_url = f"https://www.youtube.com/watch?v={urllib.parse.quote(video_id)}"
    try:
        html_text = _urlopen_with_browser_headers(page_url)
    except Exception:
        return []

    player_response = _parse_yt_initial_player_response(html_text)
    if not player_response:
        return []

    return (
        player_response
        .get("captions", {})
        .get("playerCaptionsTracklistRenderer", {})
        .get("captionTracks", [])
    )


def _choose_best_caption_track(tracks, lang="en"):
    if not tracks:
        return None

    exact = [t for t in tracks if t.get("languageCode") == lang and t.get("kind") != "asr"]
    if exact:
        return exact[0]

    fallback = [t for t in tracks if t.get("languageCode") == lang]
    if fallback:
        return fallback[0]

    return tracks[0]


def fetch_transcript(video_id, lang="en"):
    api = YouTubeTranscriptApi()
    try:
        transcript_items = api.fetch(video_id, languages=[lang])
    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable):
        transcript_items = None

    if transcript_items:
        items = []
        full_text = []
        for item in transcript_items:
            items.append({
                "start": float(getattr(item, "start", 0)),
                "duration": float(getattr(item, "duration", 0)),
                "text": getattr(item, "text", ""),
            })
            full_text.append(getattr(item, "text", ""))
        return {"available": True, "items": items, "text": "\n".join(full_text)}

    try:
        transcript_list = api.list(video_id)
        transcript = None
        try:
            transcript = transcript_list.find_transcript([lang])
        except Exception:
            pass

        if not transcript:
            try:
                transcript = transcript_list.find_generated_transcript([lang])
            except Exception:
                pass

        if not transcript:
            try:
                transcript = transcript_list.find_manually_created_transcript([lang])
            except Exception:
                pass

        if not transcript:
            transcript = next(iter(transcript_list), None)

        if transcript:
            transcript_items = transcript.fetch()
            items = []
            full_text = []
            for item in transcript_items:
                items.append({
                    "start": float(getattr(item, "start", 0)),
                    "duration": float(getattr(item, "duration", 0)),
                    "text": getattr(item, "text", ""),
                })
                full_text.append(getattr(item, "text", ""))
            return {"available": True, "items": items, "text": "\n".join(full_text)}
    except Exception:
        pass

    transcript_url = f"https://video.google.com/timedtext?lang={urllib.parse.quote(lang)}&v={urllib.parse.quote(video_id)}"
    try:
        with urllib.request.urlopen(transcript_url, timeout=10) as response:
            xml_text = response.read().decode("utf-8")
    except Exception:
        xml_text = ""

    if not xml_text or "<transcript" not in xml_text:
        tracks = _fetch_caption_tracks_from_watch_page(video_id)
        track = _choose_best_caption_track(tracks, lang=lang)
        if track and track.get("baseUrl"):
            try:
                xml_text = _urlopen_with_browser_headers(track["baseUrl"])
            except Exception:
                xml_text = ""

    if not xml_text or "<transcript" not in xml_text:
        return None

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return None

    items = []
    full_text = []
    for element in root.findall("text"):
        content = html.unescape(element.text or "")
        start = float(element.attrib.get("start", "0"))
        duration = float(element.attrib.get("dur", "0"))
        items.append({"start": start, "duration": duration, "text": content})
        full_text.append(content)

    return {"available": True, "items": items, "text": "\n".join(full_text)}


def fetch_youtube_video_details(video_id):
    api_url = (
        "https://www.googleapis.com/youtube/v3/videos?"
        + urllib.parse.urlencode({
            "part": "snippet,contentDetails,statistics",
            "id": video_id,
            "key": YOUTUBE_API_KEY,
        })
    )

    try:
        with urllib.request.urlopen(api_url, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return None

    items = payload.get("items", [])
    if not items:
        return None

    video = items[0]
    snippet = video.get("snippet", {})
    stats = video.get("statistics", {})
    content_details = video.get("contentDetails", {})

    return {
        "video_id": video_id,
        "title": snippet.get("title", ""),
        "description": snippet.get("description", ""),
        "channel_title": snippet.get("channelTitle", ""),
        "published_at": snippet.get("publishedAt", ""),
        "view_count": stats.get("viewCount", "0"),
        "like_count": stats.get("likeCount", "0"),
        "comment_count": stats.get("commentCount", "0"),
        "duration": parse_iso8601_duration(content_details.get("duration", "")),
        "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
        "watch_url": f"https://www.youtube.com/watch?v={video_id}",
        "embed_url": f"https://www.youtube.com/embed/{video_id}",
    }


def process_video_content(video_id):
    # Check if already processed
    response = supabase.table("ai_video_content").select("*").eq("video_id", video_id).execute()
    if response.data:
        return {"message": "Video already processed", "video_id": video_id}

    # Fetch transcript
    transcript_data = fetch_transcript(video_id)
    if not transcript_data or not transcript_data.get("available"):
        raise ValueError("Transcript not available for this video")

    transcript_raw = transcript_data["text"]

    # Chunk the transcript into ~3000 words
    words = transcript_raw.split()
    chunk_size = 3000
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    # Summarize each chunk using Gemini
    summarized_segments = []
    for chunk in chunks:
        prompt = f"Summarize the following video transcript segment in a concise manner, capturing the key points and concepts:\n\n{chunk}"
        try:
            if genai_client:
                response = genai_client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=prompt
                )
                summary = response.text.strip()
            else:
                summary = "AI summarization not available - API key not configured"
            summarized_segments.append(summary)
        except Exception as e:
            print(f"Error summarizing chunk: {e}")
            summarized_segments.append("Summary not available")

    # Aggregate into master_knowledge_base
    master_knowledge_base = "\n\n".join(summarized_segments)

    # Save to database
    data = {
        "video_id": video_id,
        "transcript_raw": transcript_raw,
        "summarized_segments": summarized_segments,
        "master_knowledge_base": master_knowledge_base
    }
    supabase.table("ai_video_content").insert(data).execute()

    return {"message": "Video processed successfully", "video_id": video_id}


@app.route('/api/youtube/video', methods=['GET'])
def get_youtube_video_details():
    video_id = request.args.get("video_id", "HcOc7P5BMi4").strip()
    if not video_id:
        return jsonify({"detail": "video_id query parameter is required"}), 400

    details = fetch_youtube_video_details(video_id)
    if not details:
        return jsonify({"detail": "Video details not found or API request failed"}), 404

    transcript = fetch_transcript(video_id)
    if transcript is None:
        transcript = {"available": False, "items": [], "text": "Transcript not available for this video."}

    details["transcript"] = transcript
    return jsonify(details), 200

@app.route('/api/videos', methods=['GET'])
def get_videos():
    category = request.args.get('category')
    
    query = supabase.table("videos").select("*")
    if category:
        query = query.eq("category", category)
    
    response = query.execute()
    videos = response.data
    
    return jsonify(videos), 200


@app.route('/api/ai/generate-quiz', methods=['POST'])
@require_auth
def generate_quiz():
    data = request.get_json()
    video_id = data.get("video_id")
    if not video_id:
        return jsonify({"detail": "video_id is required"}), 400

    # Retrieve master_knowledge_base
    response = supabase.table("ai_video_content").select("master_knowledge_base").eq("video_id", video_id).execute()
    if not response.data:
        return jsonify({"detail": "Video not processed yet. Please process the video first."}), 404

    knowledge_base = response.data[0]["master_knowledge_base"]

    # Generate quiz using Gemini
    prompt = f"Based on this summarized context of a long video, generate 5 high-quality multiple-choice questions for the user. Each question should have 4 options (A, B, C, D) with one correct answer. Format as JSON array of objects with keys: question, options (array of 4 strings), correct_answer (index 0-3).\n\nContext:\n{knowledge_base}"
    try:
        if genai_client:
            response = genai_client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt
            )
            quiz_text = response.text.strip()
        else:
            return jsonify({"detail": "AI features not available - API key not configured"}), 500
        # Assume Gemini returns valid JSON
        quiz = json.loads(quiz_text)
        return jsonify({"video_id": video_id, "quiz": quiz}), 200
    except Exception as e:
        print(f"Error generating quiz: {e}")
        return jsonify({"detail": "Failed to generate quiz"}), 500


@app.route('/api/ai/process-video', methods=['POST'])
@require_auth
def process_video():
    data = request.get_json()
    video_id = data.get("video_id")
    if not video_id:
        return jsonify({"detail": "video_id is required"}), 400

    try:
        result = process_video_content(video_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"detail": str(e)}), 400
    except Exception as e:
        print(f"Error processing video: {e}")
        return jsonify({"detail": "Failed to process video"}), 500


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"detail": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"detail": "Method not allowed"}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"detail": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8000)
