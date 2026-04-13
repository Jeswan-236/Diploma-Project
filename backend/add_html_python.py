import os
import psycopg2
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

def add_missing():
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found in .env")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        videos_to_insert = [
            {
                "title": "HTML Tutorial for Beginners - Full Course",
                "category": "coding",
                "language": "html",
                "duration": "2:04:14",
                "youtube_id": "qz0aGYrrlhU",
                "url": "https://www.youtube.com/watch?v=qz0aGYrrlhU",
                "description": "Learn HTML in this complete crash course for absolute beginners. You will learn all basic tags.",
                "thumbnail_url": "https://img.youtube.com/vi/qz0aGYrrlhU/hqdefault.jpg"
            },
            {
                "title": "Python for Beginners - Full Course",
                "category": "coding",
                "language": "python",
                "duration": "4:26:51",
                "youtube_id": "rfscVS0vtbw",
                "url": "https://www.youtube.com/watch?v=rfscVS0vtbw",
                "description": "This Python tutorial for beginners will help you learn Python programming from scratch.",
                "thumbnail_url": "https://img.youtube.com/vi/rfscVS0vtbw/hqdefault.jpg"
            }
        ]

        for video in videos_to_insert:
            # Check if exists
            cur.execute("SELECT id FROM videos WHERE youtube_id = %s;", (video['youtube_id'],))
            if cur.fetchone():
                print(f"Skipping (already exists): {video['title']}")
                continue

            cur.execute("""
                INSERT INTO videos (title, category, language, duration, youtube_id, url, description, thumbnail_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                video['title'], video['category'], video['language'], 
                video['duration'], video['youtube_id'], video['url'],
                video['description'], video['thumbnail_url']
            ))
            print(f"Inserted: {video['title']}")

        conn.commit()
        print("\n--- HTML & Python Added Successfully! ---")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    add_missing()
