import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

def verify():
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found in .env")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        print("--- Verifying Videos Table ---")
        cur.execute("SELECT title, category, language, duration, youtube_id FROM videos WHERE category = 'coding' ORDER BY language;")
        rows = cur.fetchall()

        if not rows:
            print("No coding videos found!")
        else:
            print(f"Found {len(rows)} coding videos:")
            for row in rows:
                print(f"- Title: {row[0]}")
                print(f"  Category: {row[1]}, Language: {row[2]}, Duration: {row[3]}, YT ID: {row[4]}")
                print("-" * 30)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    verify()
