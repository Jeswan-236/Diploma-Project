import os
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_ANON_KEY")
supabase = create_client(url, key)

try:
    # PostgREST doesn't have a direct 'show tables' but we can try to hit the root
    res = supabase.table("videos").select("count", count="exact").limit(1).execute()
    print("Videos table exists.")
except Exception as e:
    print("Videos table error:", e)

try:
    res = supabase.table("ai_video_content").select("count", count="exact").limit(1).execute()
    print("ai_video_content table exists.")
except Exception as e:
    print("ai_video_content table error:", e)

try:
    res = supabase.table("ai_video_table").select("count", count="exact").limit(1).execute()
    print("ai_video_table table exists.")
except Exception as e:
    print("ai_video_table table error:", e)
