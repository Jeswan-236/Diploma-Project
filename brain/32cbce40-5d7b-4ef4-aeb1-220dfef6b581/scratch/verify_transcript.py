import httpx
import jwt
from datetime import datetime, timedelta

# Settings from .env (retrieved in previous step)
SECRET_KEY = "9a2b5e7d1c8f304192b67f185c6023194a73e861d8f793b2184cf072289f61b3"
ALGORITHM = "HS256"

def generate_test_token():
    payload = {
        "sub": "test-user-id",
        "email": "test@example.com",
        "exp": datetime.utcnow() + timedelta(minutes=60)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def test_youtube_video_endpoint(video_id):
    token = generate_test_token()
    url = f"http://127.0.0.1:8000/api/youtube/video?video_id={video_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print(f"Testing endpoint with video_id: {video_id}...")
    try:
        with httpx.Client() as client:
            response = client.get(url, headers=headers)
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                transcript = data.get("transcript", {})
                print(f"Transcript available: {transcript.get('available')}")
                print(f"Transcript source: {transcript.get('source', 'youtube (not cached)')}")
                if transcript.get('available'):
                    text = transcript.get('text', '')
                    print(f"Transcript snippet: {text[:100]}...")
                else:
                    print(f"Transcript error: {transcript.get('text')}")
            else:
                print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    # Test with a known video (JavaScript tutorial) - PkZNo7MFNFg
    test_youtube_video_endpoint("PkZNo7MFNFg")
