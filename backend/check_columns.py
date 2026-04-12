import os
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_ANON_KEY")
supabase = create_client(url, key)

try:
    # Try to select the new columns
    res = supabase.table("ai_video_table").select("transcript_raw, summarized_segments").limit(1).execute()
    print("Columns exist!")
except Exception as e:
    print("Columns missing or error:", e)
