import os
import json
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client

sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_ANON_KEY'])

video_ids = ['PkZNo7MFNFg', 'gOK4p5bBmcQ', 'DsAuX8ExDZc', 'UukVP7Mg3TU']

for vid in video_ids:
    data = {
        "video_id": vid,
        "transcript_raw": f"Welcome to the course for {vid}! This transcript is automatically generated and provided as a fallback sample because YouTube API is currently rate limiting this cloud environment (IP block 429). In this course we will learn fundamental concepts. Feel free to mark this video as complete or click 'AI Learn' to process its data!",
        "summarized_segments": ["Introduction to course", "Core fundamental concepts"],
        "master_knowledge_base": "Cache knowledge base for offline use."
    }
    
    # Try inserting/upserting to the new unified table
    try:
        sb.table('ai_video_table').upsert(data).execute()
        print(f"Inserted mock transcript for {vid}")
    except Exception as e:
        print(f"Could not insert {vid}: {e}")
