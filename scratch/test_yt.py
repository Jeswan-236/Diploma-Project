from youtube_transcript_api import YouTubeTranscriptApi

video_id = "PkZNo7MFNFg"
try:
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    print(f"Type: {type(transcript)}")
    if transcript:
        print(f"First item type: {type(transcript[0])}")
        print(f"First item: {transcript[0]}")
except Exception as e:
    print(f"Error: {e}")
