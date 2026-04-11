
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(video_id):
    print(f"Testing /api/youtube/video?video_id={video_id}")
    try:
        resp = requests.get(f"{BASE_URL}/api/youtube/video?video_id={video_id}")
        if resp.status_code == 200:
            data = resp.json()
            transcript = data.get("transcript", {})
            available = transcript.get("available")
            source = transcript.get("source")
            text_len = len(transcript.get("text", ""))
            print(f"SUCCESS: available={available}, source={source}, text_length={text_len}")
            if text_len > 0:
                print(f"Sample: {transcript.get('text', '')[:100]}...")
        else:
            print(f"FAILED: status={resp.status_code}, detail={resp.text}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    # Test a video that SHOULD be in the database
    test_endpoint("PkZNo7MFNFg")
