import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

def add_languages():
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found in .env")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        print("--- Adding Java, PHP, and C++ tutorials ---")
        
        videos_to_insert = [
            {
                "title": "Java Tutorial for Beginners",
                "category": "coding",
                "language": "java",
                "duration": "2:30:48",
                "youtube_id": "eIrMbAQSU34",
                "url": "https://www.youtube.com/watch?v=eIrMbAQSU34",
                "description": "High-quality Java tutorial covering the fundamentals of Java programming. Perfect for absolute beginners.",
                "thumbnail_url": "https://img.youtube.com/vi/eIrMbAQSU34/hqdefault.jpg"
            },
            {
                "title": "PHP Programming Language Tutorial - Full Course",
                "category": "coding",
                "language": "php",
                "duration": "4:36:40",
                "youtube_id": "OK_JCtrrv-c",
                "url": "https://www.youtube.com/watch?v=OK_JCtrrv-c",
                "description": "This course will give you a full introduction into all of the core concepts in PHP.",
                "thumbnail_url": "https://img.youtube.com/vi/OK_JCtrrv-c/hqdefault.jpg"
            },
            {
                "title": "C++ Full Course for free",
                "category": "coding",
                "language": "cpp",
                "duration": "6:00:15",
                "youtube_id": "vLnPwxZdW4Y",
                "url": "https://www.youtube.com/watch?v=vLnPwxZdW4Y",
                "description": "Comprehensive C++ tutorial for beginners. Learn variables, loops, arrays, and more.",
                "thumbnail_url": "https://img.youtube.com/vi/vLnPwxZdW4Y/hqdefault.jpg"
            }
        ]

        for video in videos_to_insert:
            # Check if already exists to avoid duplicates
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
        print("\n--- Additional Languages Added Successfully! ---")

    except Exception as e:
        print(f"An error occurred: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    add_languages()
