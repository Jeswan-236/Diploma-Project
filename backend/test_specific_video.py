import jwt
import os
import urllib.request
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# Create a valid token for 'aruvajaswan' (the user in the logs)
def create_test_token():
    payload = {
        "sub": "aruvajaswan",
        "exp": datetime.utcnow() + timedelta(minutes=10)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def test_video_load(video_id):
    token = create_test_token()
    url = f"http://127.0.0.1:8000/api/youtube/video?video_id={video_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"--- Pinging API for video: {video_id} ---")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            print(f"Status: {response.status}")
            print(f"Title: {data.get('title')}")
            print(f"Transcript available: {data.get('transcript', {}).get('available')}")
            print(f"Transcript Preview: {data.get('transcript', {}).get('text')[:200]}...")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_video_load("OXGznpKZ_sA")
