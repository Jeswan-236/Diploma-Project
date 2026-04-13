import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('.env')
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

cur.execute("SELECT id, title, youtube_id FROM videos WHERE language IN ('html', 'python')")
videos = cur.fetchall()

if not videos:
    print("Videos not found!")

for v in videos:
    vid_id, title, yid = v
    print(f"\n--- Checking '{title}' ---")
    
    # Check ai_video_table 
    cur.execute("SELECT status, transcript_raw IS NOT NULL FROM ai_video_table WHERE video_id = %s", (str(vid_id),))
    rag = cur.fetchone()
    if rag:
        print(f"[ai_video_table]: Status = {rag[0]}, Has Transcript = {rag[1]}")
    else:
        print("[ai_video_table]: Missing (Not Embedded)")

conn.close()
