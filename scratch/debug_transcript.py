
import sys
import os
import urllib.parse
import urllib.request
import json

# Mocking enough of main.py to test fetch_transcript
DATABASE_URL = "mock"
YOUTUBE_API_KEY = "mock"

def _choose_best_caption_track(tracks, lang="en"):
    if not tracks: return None
    exact = [t for t in tracks if t.get("languageCode") == lang and t.get("kind") != "asr"]
    if exact: return exact[0]
    fallback = [t for t in tracks if t.get("languageCode") == lang]
    if fallback: return fallback[0]
    return tracks[0]

# Import the actual function from main.py if possible, or copy it here.
# Since importing main.py might have side effects (FastAPI init), 
# I will copy the current logic from main.py to verify it exactly as it is.

def fetch_transcript_debug(video_id, lang="en"):
    try:
        from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
        api = YouTubeTranscriptApi()
        
        transcript_data = None
        try:
            print(f"DEBUG: Trying api.fetch for {video_id} with lang {lang}")
            transcript_obj = api.fetch(video_id, languages=[lang])
            print(f"DEBUG: api.fetch returned {type(transcript_obj)}")
            transcript_data = transcript_obj.to_raw_data()
            print(f"DEBUG: transcript_data length: {len(transcript_data) if transcript_data else 0}")
        except Exception as e:
            print(f"DEBUG: api.fetch failed: {type(e).__name__}: {e}")
            try:
                print(f"DEBUG: Trying api.list for {video_id}")
                transcript_list = api.list(video_id)
                try:
                    print(f"DEBUG: Trying find_transcript")
                    transcript_data = transcript_list.find_transcript([lang]).fetch().to_raw_data()
                except Exception as e2:
                    print(f"DEBUG: find_transcript failed: {e2}")
                    try:
                        print(f"DEBUG: Trying find_generated_transcript")
                        transcript_data = transcript_list.find_generated_transcript([lang]).fetch().to_raw_data()
                    except Exception as e3:
                        print(f"DEBUG: find_generated_transcript failed: {e3}")
                        # Final fallback: pick the first available
                        try:
                            first = next(iter(transcript_list))
                            print(f"DEBUG: Trying fallback to first transcript: {first.language_code}")
                            transcript_data = first.fetch().to_raw_data()
                        except Exception as e4:
                            print(f"DEBUG: first fallback failed: {e4}")
                            transcript_data = None
            except Exception as e_list:
                print(f"DEBUG: api.list failed: {type(e_list).__name__}: {e_list}")
                transcript_data = None

        if transcript_data:
            return {"available": True, "text_len": sum(len(item.get("text", "")) for item in transcript_data)}

    except Exception as e:
        print(f"DEBUG: Global exception: {e}")

    return {"available": False}

if __name__ == "__main__":
    test_video = "PkZNo7MFNFg" # JavaScript course
    result = fetch_transcript_debug(test_video)
    print(f"RESULT: {result}")
