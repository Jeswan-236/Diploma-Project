import urllib.request
import json

try:
    url = 'http://127.0.0.1:8000/api/youtube/video?video_id=dQw4w9WgXcQ'
    print(f"Testing URL: {url}")
    with urllib.request.urlopen(url, timeout=30) as r:
        data = json.loads(r.read().decode('utf-8'))
        print(f"Status Code: {r.status}")
        transcript = data.get("transcript", {})
        available = transcript.get("available")
        source = transcript.get("source", "youtube")
        print(f"Transcript Available: {available}")
        print(f"Source: {source}")
        if available:
            print(f"Snippet: {transcript.get('text', '')[:100]}...")
except Exception as e:
    print(f"Error: {e}")
