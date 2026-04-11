import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "backend/.env"))
db_url = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS enrollments (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        username TEXT NOT NULL,
        video_id TEXT NOT NULL,
        title TEXT,
        enrolled_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        UNIQUE(username, video_id)
    );
    ''')
    conn.commit()
    print("Table created successfully")
except Exception as e:
    print("Error:", e)
finally:
    if 'conn' in locals():
        conn.close()
