
import sys
import os

# Add venv to path if needed (it should be handled by the runner)
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    
    print("YouTubeTranscriptApi imported successfully.")
    api = YouTubeTranscriptApi()
    
    print(f"Methods of YouTubeTranscriptApi instance: {[m for m in dir(api) if not m.startswith('_')]}")
    
    # Check if fetch exists and its signature
    import inspect
    if hasattr(api, 'fetch'):
        print(f"fetch signature: {inspect.signature(api.fetch)}")
    else:
        print("fetch method not found on instance.")
        
    print(f"Static methods: {[m for m in dir(YouTubeTranscriptApi) if not m.startswith('_')]}")

except Exception as e:
    print(f"Error: {e}")
