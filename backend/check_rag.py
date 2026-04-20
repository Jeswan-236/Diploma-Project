import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 1. Check ai_video_table
res = supabase.table("ai_video_table").select("video_id, status").execute()
videos = res.data
print(f"Total videos in ai_video_table: {len(videos)}")
for v in videos:
    print(f" - {v['video_id']}: {v['status']}")

# 2. Check storage bucket
bucket_name = 'rag-embeddings-bucket'
try:
    files = supabase.storage.from_(bucket_name).list()
    print(f"\nFiles in bucket '{bucket_name}': {len(files)}")
    for f in files:
        print(f" - {f['name']}")
except Exception as e:
    print(f"\nBucket check error: {e}")
