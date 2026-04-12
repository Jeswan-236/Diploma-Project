import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import fetch_transcript

video_id = 'dQw4w9WgXcQ'
print(f"Testing fetch_transcript for {video_id}...")
result = fetch_transcript(video_id)
if result:
    print(f"Success! Available: {result.get('available')}")
    print(f"Text length: {len(result.get('text', ''))}")
    print(f"Source example: {result.get('text', '')[:100]}")
else:
    print("Failed to fetch transcript.")
