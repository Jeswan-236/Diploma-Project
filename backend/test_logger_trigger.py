import urllib.request
import os
import json
from dotenv import load_dotenv

# We need a real token or bypass the authorization check for a moment to test the logger
# Since I am on the server, I'll just hit it.
# Actually, I'll use a valid-looking Bearer if I can find one, or just hit an endpoint that logs.

url = "http://127.0.0.1:8000/api/youtube/video?video_id=PkZNo7MFNFg"
headers = {"Authorization": "Bearer test_token"}

print(f"Pinging {url}...")
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        print(f"Status: {response.status}")
        print(f"Body: {response.read().decode()[:200]}...")
except Exception as e:
    print(f"Error: {e}")
