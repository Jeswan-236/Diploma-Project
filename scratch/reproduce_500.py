import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from main import fetch_transcript
    
    video_id = "PkZNo7MFNFg"
    print(f"Testing fetch_transcript for {video_id}...")
    result = fetch_transcript(video_id)
    print("Success!")
    print(f"Transcript available: {result['available']}")
    print(f"Text length: {len(result['text'])}")
except Exception as e:
    print(f"Caught Exception: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
