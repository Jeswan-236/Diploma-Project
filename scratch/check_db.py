
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Path to .env from scratch/check_db.py
env_path = os.path.join(os.path.dirname(__file__), "../backend/.env")
print(f"Loading env from: {os.path.abspath(env_path)}")
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
# The actual keys in .env are usually SUPABASE_URL and SUPABASE_ANON_KEY
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print(f"Missing credentials: URL={SUPABASE_URL}, KEY={'Found' if SUPABASE_KEY else 'Missing'}")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_db():
    print("Checking ai_video_content table...")
    try:
        res = supabase.table("ai_video_content").select("video_id").execute()
        if res.data:
            print(f"Total videos in ai_video_content: {len(res.data)}")
            for row in res.data[:5]:
                print(f" - {row['video_id']}")
        else:
            print("No data found in ai_video_content.")
    except Exception as e:
        print(f"DB Error: {e}")

if __name__ == "__main__":
    check_db()
