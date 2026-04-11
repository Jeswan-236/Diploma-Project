import os
import uuid
import httpx
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
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
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

CORS(app, resources={r"/api/*": {"origins": allow_origins, "allow_headers": ["Content-Type", "Authorization", "Accept", "User-Agent"], "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]}}, supports_credentials=True)

# Password & JWT utilities
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def normalize_password(password):
    if isinstance(password, str):
        return password[:72]
    return password


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(normalize_password(plain_password), hashed_password)

def get_password_hash(password):
    return pwd_context.hash(normalize_password(password))

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

    thumbnail_url = data.get('thumbnail_url')
    if not thumbnail_url:
        thumbnail_url = get_youtube_thumbnail_url(data['url'])

    new_video = {
        "title": data['title'],
        "description": data.get('description', ''),
        "url": data['url'],
        "category": data['category'],
        "keywords": data.get('keywords', ''),
        "thumbnail_url": thumbnail_url
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
    elif 'url' in data:
        thumbnail_url = get_youtube_thumbnail_url(data['url'])
        if thumbnail_url:
            update_data['thumbnail_url'] = thumbnail_url
    
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

@app.route('/api/admin/videos/fill-thumbnails', methods=['POST'])
@require_auth
@require_admin
def fill_missing_video_thumbnails(current_user):
    response = supabase.table("videos").select("id,url,thumbnail_url").execute()
    if not response.data:
        return jsonify({"message": "No videos found."}), 200

    updated_count = 0
    for video in response.data:
        if video.get('thumbnail_url'):
            continue
        thumbnail_url = get_youtube_thumbnail_url(video.get('url'))
        if not thumbnail_url:
            continue
        supabase.table("videos").update({"thumbnail_url": thumbnail_url}).eq("id", video['id']).execute()
        updated_count += 1

    return jsonify({"message": f"Updated {updated_count} missing thumbnails."}), 200


def extract_youtube_video_id(video_url):
    if not video_url:
        return None

    match = re.search(r'(?:youtu\.be\/|youtube(?:-nocookie)?\.com\/(?:watch\?v=|embed\/|v\/|shorts\/))([A-Za-z0-9_-]{11})', video_url)
    if match:
        return match.group(1)

    try:
        parsed = urllib.parse.urlparse(video_url)
        hostname = parsed.hostname or ''
        if 'youtu.be' in hostname:
            return parsed.path.lstrip('/')
        if 'youtube.com' in hostname and parsed.query:
            query = urllib.parse.parse_qs(parsed.query)
            if 'v' in query:
                return query.get('v', [None])[0]
    except Exception:
        return None

    return None


def get_youtube_thumbnail_url(video_url):
    if not video_url:
        return None

    video_id = extract_youtube_video_id(video_url)
    if not video_id:
        # Try to resolve YouTube result/search URLs using the YouTube API
        try:
            parsed = urllib.parse.urlparse(video_url)
            hostname = parsed.hostname or ''
            if 'youtube.com' in hostname:
                query = urllib.parse.parse_qs(parsed.query)
                search_query = query.get('search_query', [None])[0] or query.get('q', [None])[0]
                if search_query:
                    video_id = search_youtube_video(search_query)
        except Exception:
            video_id = None

    if not video_id:
        return None

    return f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg'

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

    # 1. Exact match for requested language (manual)
    exact = [t for t in tracks if t.get("languageCode") == lang and t.get("kind") != "asr"]
    if exact:
        return exact[0]

    # 2. Match with prefix (e.g., 'en' matches 'en-US') for manual
    prefix_match = [t for t in tracks if t.get("languageCode", "").startswith(lang) and t.get("kind") != "asr"]
    if prefix_match:
        return prefix_match[0]

    # 3. Any match for requested language (including auto-generated)
    any_match = [t for t in tracks if t.get("languageCode") == lang]
    if any_match:
        return any_match[0]

    # 4. Any prefix match (including auto-generated)
    any_prefix = [t for t in tracks if t.get("languageCode", "").startswith(lang)]
    if any_prefix:
        return any_prefix[0]

    # 5. Final fallback: pick first available
    return tracks[0]


def fetch_transcript(video_id, lang="en"):
    """
    Fetches the transcript for a YouTube video using the youtube-transcript-api library.
    Handles various library version differences and YouTube IP blocking issues.
    """
    try:
        # Instantiate the API client
        from youtube_transcript_api import YouTubeTranscriptApi
        api = YouTubeTranscriptApi()
        
        transcript_data = None
        try:
            print(f"Transcript Fetch: Trying primary API for {video_id} (lang: {lang})")
            # 1. Try to fetch the transcript in the requested language
            transcript_obj = api.fetch(video_id, languages=[lang])
            transcript_data = transcript_obj.to_raw_data()
        except Exception as e:
            print(f"Transcript Fetch: Primary language '{lang}' failed: {e}")
            # 2. If requested language fails, try to list all and pick the best one
            try:
                print(f"Transcript Fetch: Listing all available transcripts for {video_id}...")
                transcript_list = api.list(video_id)
                # Try finding specified language
                try:
                    transcript_data = transcript_list.find_transcript([lang]).fetch().to_raw_data()
                except Exception:
                    try:
                        # Fallback to generated
                        transcript_data = transcript_list.find_generated_transcript([lang]).fetch().to_raw_data()
                    except Exception:
                        # Final fallback: pick the first available
                        transcript_data = next(iter(transcript_list)).fetch().to_raw_data()
            except Exception as e_list:
                print(f"Transcript Fetch: API listing failed: {e_list}")
                transcript_data = None

        if transcript_data:
            items = []
            full_text = []
            for item in transcript_data:
                # In to_raw_data(), it's a list of dictionaries
                start = float(item.get("start", 0))
                duration = float(item.get("duration", 0))
                text = item.get("text", "")
                
                items.append({
                    "start": start,
                    "duration": duration,
                    "text": text,
                })
                full_text.append(text)
            
            return {"available": True, "items": items, "text": "\n".join(full_text)}

    except Exception as e:
        # This catches RequestBlocked (IP bans) and other library-specific exceptions
        print(f"YouTube Transcript API CRITICAL ERROR for {video_id}: {e}")

    # --- FALLBACK 1: XML TimedText API ---
    print(f"Transcript Fetch: Attempting Fallback 1 (TimedText API) for {video_id}")
    try:
        transcript_url = f"https://video.google.com/timedtext?lang={urllib.parse.quote(lang)}&v={urllib.parse.quote(video_id)}"
        with urllib.request.urlopen(transcript_url, timeout=10) as response:
            xml_text = response.read().decode("utf-8")
        
        if xml_text and "<transcript" in xml_text:
            return _parse_xml_transcript(xml_text)
    except Exception:
        pass

    # --- FALLBACK 2: Scrape watch page for caption tracks ---
    print(f"Transcript Fetch: Attempting Fallback 2 (Watch Page Scraping) for {video_id}")
    try:
        tracks = _fetch_caption_tracks_from_watch_page(video_id)
        track = _choose_best_caption_track(tracks, lang=lang)
        if track and track.get("baseUrl"):
            xml_text = _urlopen_with_browser_headers(track["baseUrl"])
            if xml_text and "<transcript" in xml_text:
                return _parse_xml_transcript(xml_text)
    except Exception:
        pass

    return None


def _parse_xml_transcript(xml_text):
    """Helper to parse YouTube XML transcript format."""
    try:
        root = ET.fromstring(xml_text)
        items = []
        full_text = []
        for element in root.findall("text"):
            content = html.unescape(element.text or "")
            start = float(element.attrib.get("start", "0"))
            duration = float(element.attrib.get("dur", "0"))
            items.append({"start": start, "duration": duration, "text": content})
            full_text.append(content)
        return {"available": True, "items": items, "text": "\n".join(full_text)}
    except Exception:
        return None


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
    except Exception as e:
        print(f"Error fetching video details for {video_id}: {e}")
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


def search_youtube_video(query):
    query = query.strip()
    if not query:
        return None

    search_url = (
        "https://www.googleapis.com/youtube/v3/search?"
        + urllib.parse.urlencode({
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": 1,
            "key": YOUTUBE_API_KEY,
        })
    )

    try:
        with urllib.request.urlopen(search_url, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return None

    items = payload.get("items", [])
    if not items:
        return None

    first_item = items[0].get("id", {})
    return first_item.get("videoId")


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
    video_id = request.args.get("video_id", "").strip()
    query = request.args.get("query", "").strip()

    if not video_id and not query:
        return jsonify({"detail": "video_id or query parameter is required"}), 400

    if not video_id and query:
        video_id = search_youtube_video(query)
        if not video_id:
            return jsonify({"detail": "Could not find a video for the given query"}), 404

    details = fetch_youtube_video_details(video_id)
    if not details:
        return jsonify({"detail": "Video details not found or API request failed"}), 404

    # --- DATABASE-FIRST LOOKUP ---
    print(f"Checking database for existing transcript: {video_id}")
    try:
        db_res = supabase.table("ai_video_content").select("transcript_raw").eq("video_id", video_id).execute()
        if db_res.data and len(db_res.data) > 0:
            print(f"Found existing transcript in database for {video_id}")
            transcript = {
                "available": True,
                "items": [], # We don't store segments currently, but this fulfills the interface
                "text": db_res.data[0].get("transcript_raw", ""),
                "source": "database"
            }
        else:
            print(f"No existing transcript in database for {video_id}. Fetching from YouTube.")
            transcript = fetch_transcript(video_id)
    except Exception as e:
        print(f"Database lookup error specifically for transcript: {e}")
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


@app.route('/api/courses', methods=['GET'])
def get_courses():
    category = request.args.get('category')
    level = request.args.get('level')

    try:
        query = supabase.table("courses").select("*")
        if category:
            query = query.eq("category", category)
        if level:
            query = query.eq("level", level)
        response = query.execute()
        if response.data is not None:
            return jsonify(response.data), 200
    except Exception as e:
        print("Could not load courses from Supabase:", e)

    sample_courses = [
        {
            "id": "course-html-basics",
            "title": "HTML Fundamentals",
            "description": "Build strong HTML foundations with pages, forms, tables, and semantic structure.",
            "category": "Frontend",
            "level": "Basic",
            "duration": "3 hours",
            "lessons": 12,
            "resources": ["HTML cheatsheet", "Responsive markup examples"],
            "thumbnail_url": "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=800&q=80"
        },
        {
            "id": "course-css-essentials",
            "title": "CSS Essentials",
            "description": "Learn styling, layouts, flexbox, grid, and modern responsive design techniques.",
            "category": "Frontend",
            "level": "Advanced",
            "duration": "4 hours",
            "lessons": 15,
            "resources": ["CSS layout guide", "Animation snippets"],
            "thumbnail_url": "https://images.unsplash.com/photo-1517430816045-df4b7de11d1f?auto=format&fit=crop&w=800&q=80"
        },
        {
            "id": "course-js-core",
            "title": "JavaScript Core",
            "description": "Master the JavaScript language, DOM manipulation, async programming, and practical project work.",
            "category": "Frontend",
            "level": "Professional",
            "duration": "5 hours",
            "lessons": 18,
            "resources": ["JS interview questions", "Async/await exercises"],
            "thumbnail_url": "https://images.unsplash.com/photo-1518773553398-650c184e0bb3?auto=format&fit=crop&w=800&q=80"
        },
        {
            "id": "course-db-fundamentals",
            "title": "Database Fundamentals",
            "description": "Explore SQL, relational design, queries, joins, and the foundations of data storage.",
            "category": "Database",
            "level": "Basic",
            "duration": "3 hours",
            "lessons": 10,
            "resources": ["SQL syntax guide", "Normalization examples"],
            "thumbnail_url": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=800&q=80"
        },
        {
            "id": "course-python-start",
            "title": "Python for Beginners",
            "description": "Start coding in Python with variables, functions, loops, and real-world examples.",
            "category": "Programming",
            "level": "Basic",
            "duration": "4 hours",
            "lessons": 14,
            "resources": ["Python cheat sheet", "Mini projects"],
            "thumbnail_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80"
        },
        {
            "id": "course-java-oop",
            "title": "Java OOP & Projects",
            "description": "Learn object-oriented programming in Java and build real-world applications step by step.",
            "category": "Programming",
            "level": "Advanced",
            "duration": "5 hours",
            "lessons": 16,
            "resources": ["OOP patterns", "Project templates"],
            "thumbnail_url": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=800&q=80"
        }
    ]

    if category:
        sample_courses = [course for course in sample_courses if course["category"] == category]
    if level:
        sample_courses = [course for course in sample_courses if course["level"] == level]

    return jsonify(sample_courses), 200


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


# ====================== RAG PIPELINE UTILITIES ======================

RAG_BUCKET_NAME = "rag-embeddings-bucket"
OPENROUTER_EMBEDDINGS_URL = "https://openrouter.ai/api/v1/embeddings"
OPENROUTER_EMBEDDING_MODEL = "openai/text-embedding-3-small"


def chunk_transcript(text, chunk_size=800, overlap=150):
    """
    Split transcript text into semantic chunks using a character-based
    recursive approach. Splits on paragraph breaks first, then sentences,
    then falls back to character boundaries. Overlap ensures context is
    preserved across chunk boundaries.
    """
    if not text or not text.strip():
        return []

    text = text.strip()

    # If text fits in one chunk, return as-is
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        if end >= len(text):
            chunks.append(text[start:].strip())
            break

        # Try to find a natural break point (paragraph, sentence, word)
        segment = text[start:end]

        # Priority 1: paragraph break
        para_break = segment.rfind('\n\n')
        if para_break > chunk_size * 0.3:
            end = start + para_break + 2
        else:
            # Priority 2: sentence break (. ! ?)
            sentence_break = max(
                segment.rfind('. '),
                segment.rfind('! '),
                segment.rfind('? ')
            )
            if sentence_break > chunk_size * 0.3:
                end = start + sentence_break + 2
            else:
                # Priority 3: word break
                word_break = segment.rfind(' ')
                if word_break > chunk_size * 0.3:
                    end = start + word_break + 1
                # else: hard cut at chunk_size

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move start forward, applying overlap
        start = max(start + 1, end - overlap)

    return chunks


def generate_embeddings_openrouter(text_chunks):
    """
    Call the OpenRouter embeddings API to generate vector embeddings
    for each text chunk. Returns a list of dicts with 'text' and 'embedding' keys.
    Raises an exception if the API call fails.
    """
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY is not configured in environment variables.")

    if not text_chunks:
        raise ValueError("No text chunks provided for embedding generation.")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://skillstalker.app",
        "X-Title": "SkillStalker RAG Pipeline"
    }

    payload = {
        "model": OPENROUTER_EMBEDDING_MODEL,
        "input": text_chunks
    }

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                OPENROUTER_EMBEDDINGS_URL,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as e:
        error_body = e.response.text
        print(f"OpenRouter API error ({e.response.status_code}): {error_body}")
        raise ValueError(f"OpenRouter embeddings API returned {e.response.status_code}: {error_body}")
    except httpx.RequestError as e:
        print(f"OpenRouter request error: {e}")
        raise ValueError(f"Failed to connect to OpenRouter API: {str(e)}")

    result = response.json()
    embeddings_data = result.get("data", [])

    if len(embeddings_data) != len(text_chunks):
        raise ValueError(
            f"Embedding count mismatch: got {len(embeddings_data)} embeddings "
            f"for {len(text_chunks)} chunks."
        )

    # Pair each chunk text with its embedding vector
    paired = []
    for i, chunk_text in enumerate(text_chunks):
        embedding_obj = embeddings_data[i]
        paired.append({
            "chunk_index": i,
            "text": chunk_text,
            "embedding": embedding_obj.get("embedding", [])
        })

    return paired


def upload_embeddings_to_supabase_storage(video_id, embeddings_json):
    """
    Upload the embeddings JSON file to a Supabase Storage bucket.
    Returns the file path within the bucket.
    """
    file_name = f"{video_id}_embeddings.json"
    file_content = json.dumps(embeddings_json, ensure_ascii=False).encode("utf-8")

    try:
        # Attempt to upload (will create/overwrite the file)
        supabase.storage.from_(RAG_BUCKET_NAME).upload(
            path=file_name,
            file=file_content,
            file_options={"content-type": "application/json", "upsert": "true"}
        )
    except Exception as e:
        error_str = str(e)
        # If the file already exists and upsert didn't work, try update
        if "Duplicate" in error_str or "already exists" in error_str.lower():
            try:
                supabase.storage.from_(RAG_BUCKET_NAME).update(
                    path=file_name,
                    file=file_content,
                    file_options={"content-type": "application/json"}
                )
            except Exception as update_err:
                print(f"Supabase Storage update error: {update_err}")
                raise ValueError(f"Failed to upload/update embeddings file: {update_err}")
        else:
            print(f"Supabase Storage upload error: {e}")
            raise ValueError(f"Failed to upload embeddings file to storage: {e}")

    # Build the public URL or file reference
    try:
        public_url_resp = supabase.storage.from_(RAG_BUCKET_NAME).get_public_url(file_name)
        file_url = public_url_resp if isinstance(public_url_resp, str) else public_url_resp.get("publicURL", f"{RAG_BUCKET_NAME}/{file_name}")
    except Exception:
        file_url = f"{RAG_BUCKET_NAME}/{file_name}"

    return file_name, file_url


def save_to_ai_video_table(video_id, file_name, file_url, chunk_count):
    """
    Insert or update a record in the ai_video_table to serve as the
    RAG index linking video IDs to their embedding files.
    """
    record = {
        "video_id": str(video_id),
        "bucket_file_name": file_name,
        "bucket_file_url": file_url,
        "chunk_count": chunk_count,
        "status": "processed",
        "processed_at": datetime.utcnow().isoformat()
    }

    try:
        # Try to upsert (insert or update on conflict)
        existing = supabase.table("ai_video_table").select("id").eq("video_id", str(video_id)).execute()
        if existing.data:
            supabase.table("ai_video_table").update(record).eq("video_id", str(video_id)).execute()
        else:
            supabase.table("ai_video_table").insert(record).execute()
    except Exception as e:
        print(f"Supabase ai_video_table error: {e}")
        raise ValueError(f"Failed to save RAG index record: {e}")


@app.route('/api/ai/rag-process-video', methods=['POST'])
@require_auth
def rag_process_video(current_user):
    """
    RAG Pipeline Endpoint:
    1. Receives video_id + transcript from the frontend
    2. Chunks the transcript with overlap
    3. Generates embeddings via OpenRouter
    4. Uploads embeddings JSON to Supabase Storage bucket
    5. Saves the bucket reference in ai_video_table
    """
    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400

    video_id = data.get("video_id")
    transcript = data.get("transcript")

    if not video_id:
        return jsonify({"detail": "video_id is required"}), 400
    if not transcript or not transcript.strip():
        return jsonify({"detail": "transcript is required and cannot be empty"}), 400

    # Check if already processed
    try:
        existing = supabase.table("ai_video_table").select("id, status").eq("video_id", str(video_id)).execute()
        if existing.data and existing.data[0].get("status") == "processed":
            return jsonify({
                "message": "Video already processed for RAG",
                "video_id": str(video_id),
                "status": "already_processed"
            }), 200
    except Exception:
        pass  # Table may not exist yet, proceed

    # Step 1: Chunk the transcript
    try:
        chunks = chunk_transcript(transcript, chunk_size=800, overlap=150)
        if not chunks:
            return jsonify({"detail": "Transcript produced no valid chunks after processing"}), 400
        print(f"[RAG] Video {video_id}: Split into {len(chunks)} chunks")
    except Exception as e:
        print(f"[RAG] Chunking error: {e}")
        return jsonify({"detail": f"Failed to chunk transcript: {str(e)}"}), 500

    # Step 2: Generate embeddings via OpenRouter
    try:
        embeddings_paired = generate_embeddings_openrouter(chunks)
        print(f"[RAG] Video {video_id}: Generated {len(embeddings_paired)} embeddings")
    except ValueError as e:
        # OpenRouter failed — abort before writing to Supabase
        return jsonify({"detail": f"Embedding generation failed: {str(e)}"}), 502
    except Exception as e:
        print(f"[RAG] Unexpected embedding error: {e}")
        return jsonify({"detail": "Unexpected error during embedding generation"}), 500

    # Step 3: Assemble the full embeddings JSON document
    embeddings_document = {
        "video_id": str(video_id),
        "model": OPENROUTER_EMBEDDING_MODEL,
        "chunk_count": len(embeddings_paired),
        "created_at": datetime.utcnow().isoformat(),
        "chunks": embeddings_paired
    }

    # Step 4: Upload JSON to Supabase Storage
    try:
        file_name, file_url = upload_embeddings_to_supabase_storage(video_id, embeddings_document)
        print(f"[RAG] Video {video_id}: Uploaded to bucket as {file_name}")
    except ValueError as e:
        return jsonify({"detail": f"Storage upload failed: {str(e)}"}), 502
    except Exception as e:
        print(f"[RAG] Unexpected storage error: {e}")
        return jsonify({"detail": "Unexpected error during storage upload"}), 500

    # Step 5: Save reference in ai_video_table
    try:
        save_to_ai_video_table(video_id, file_name, file_url, len(embeddings_paired))
        print(f"[RAG] Video {video_id}: Saved to ai_video_table")
    except ValueError as e:
        return jsonify({"detail": f"Database save failed: {str(e)}"}), 502
    except Exception as e:
        print(f"[RAG] Unexpected DB error: {e}")
        return jsonify({"detail": "Unexpected error saving to database"}), 500

    return jsonify({
        "message": "Video processed for RAG successfully",
        "video_id": str(video_id),
        "chunk_count": len(embeddings_paired),
        "storage_file": file_name,
        "status": "processed"
    }), 200


@app.route('/api/user/enroll', methods=['POST'])
@require_auth
def enroll_user(current_user):
    data = request.get_json()
    video_id = data.get("video_id")
    title = data.get("title", "")
    
    if not video_id:
        return jsonify({"detail": "video_id required"}), 400
        
    try:
        new_enrollment = {
            "username": current_user["username"],
            "video_id": video_id,
            "title": title
        }
        resp = supabase.table("enrollments").insert(new_enrollment).execute()
        return jsonify({"message": "Successfully enrolled", "data": resp.data}), 201
    except Exception as e:
        if 'duplicate key' in str(e).lower() or '23505' in str(e):
            return jsonify({"detail": "Already enrolled"}), 400
        print(f"Enroll error: {e}")
        return jsonify({"detail": "Enrollment failed"}), 500


@app.route('/api/user/enrollments', methods=['GET'])
@require_auth
def get_user_enrollments(current_user):
    try:
        enrollments = supabase.table("enrollments").select("video_id").eq("username", current_user["username"]).execute()
        if not enrollments.data:
            return jsonify([]), 200
            
        enrolled_ids = [e["video_id"] for e in enrollments.data]
        videos = supabase.table("videos").select("*").in_("id", enrolled_ids).execute()
        return jsonify(videos.data), 200
        
    except Exception as e:
        print(f"Fetch enrollments error: {e}")
        return jsonify({"detail": "Failed to fetch enrolled modules"}), 500


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
