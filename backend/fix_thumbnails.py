import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

def fix_urls():
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found in .env")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        print("--- Fixing thumbnail URLs ---")
        cur.execute("""
            UPDATE videos
            SET thumbnail_url = CASE
                WHEN url ILIKE '%youtu.be/%' AND substring(url FROM 'youtu\.be/([^?&/]+)') IS NOT NULL THEN concat('https://img.youtube.com/vi/', substring(url FROM 'youtu\.be/([^?&/]+)'), '/hqdefault.jpg')
                WHEN url ILIKE '%youtube.com/watch%' AND substring(url FROM 'v=([^&]+)') IS NOT NULL THEN concat('https://img.youtube.com/vi/', substring(url FROM 'v=([^&]+)'), '/hqdefault.jpg')
                ELSE thumbnail_url
            END
            WHERE thumbnail_url IS NULL OR thumbnail_url LIKE '%//hqdefault.jpg%';
        """)
        print(f"Fixed {cur.rowcount} thumbnail URLs.")

        conn.commit()

    except Exception as e:
        print(f"An error occurred: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    fix_urls()
