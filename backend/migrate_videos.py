import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

def migrate():
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found in .env")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        print("--- Step 1: Updating Schema ---")
        # Add missing columns if they don't exist
        columns_to_add = [
            ("language", "TEXT"),
            ("youtube_id", "TEXT"),
            ("duration", "TEXT")
        ]
        
        for col_name, col_type in columns_to_add:
            cur.execute(f"""
                ALTER TABLE videos 
                ADD COLUMN IF NOT EXISTS {col_name} {col_type};
            """)
            print(f"Ensured column '{col_name}' exists.")

        print("\n--- Step 2: Cleaning up dummy data ---")
        # Delete existing dummy entries to avoid duplicates and replace with high-quality data
        # We target the specific categories and titles that are considered "dummy"
        dummy_titles = [
            'HTML Video Class', 'CSS Video Class', 'JavaScript Video Class', 
            'Python Video Class', 'MySQL Video Class'
        ]
        
        cur.execute("DELETE FROM videos WHERE title = ANY(%s) OR category = 'coding';", (dummy_titles,))
        print(f"Deleted {cur.rowcount} dummy/existing coding records.")

        print("\n--- Step 3: Inserting professional data ---")
        
        videos_to_insert = [
            {
                "title": "JavaScript Tutorial for Beginners: Full Course",
                "category": "coding",
                "language": "javascript",
                "duration": "7:40:00",
                "youtube_id": "PkZNo7MFNFg",
                "url": "https://www.youtube.com/watch?v=PkZNo7MFNFg",
                "description": "Comprehensive JavaScript tutorial for beginners. Covers everything from basics to advanced concepts.",
                "thumbnail_url": "https://img.youtube.com/vi/PkZNo7MFNFg/hqdefault.jpg"
            },
            {
                "title": "CSS Tutorial for Beginners - 6+ Hour Full Course",
                "category": "coding",
                "language": "css",
                "duration": "6:18:00",
                "youtube_id": "OXGznpKZ_sA",
                "url": "https://www.youtube.com/watch?v=OXGznpKZ_sA",
                "description": "Complete CSS tutorial covering styling, layout, responsive design and modern CSS features.",
                "thumbnail_url": "https://img.youtube.com/vi/OXGznpKZ_sA/hqdefault.jpg"
            },
            {
                "title": "MySQL Tutorial for Beginners [Full Course]",
                "category": "coding",
                "language": "mysql",
                "duration": "3:10:00",
                "youtube_id": "7S_tz1z_5bA",
                "url": "https://www.youtube.com/watch?v=7S_tz1z_5bA",
                "description": "Full MySQL course for beginners. Learn database design, queries, and management.",
                "thumbnail_url": "https://img.youtube.com/vi/7S_tz1z_5bA/hqdefault.jpg"
            },
            {
                "title": "19 Web Dev Projects – HTML, CSS, JavaScript Tutorial",
                "category": "coding",
                "language": "fullstack",
                "duration": "12:00:00",
                "youtube_id": "BiA08jfr4RU",
                "url": "https://www.youtube.com/watch?v=BiA08jfr4RU",
                "description": "Build 19 real-world web development projects using HTML, CSS, and JavaScript.",
                "thumbnail_url": "https://img.youtube.com/vi/BiA08jfr4RU/hqdefault.jpg"
            }
        ]

        for video in videos_to_insert:
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
        print("\n--- Migration Completed Successfully! ---")

    except Exception as e:
        print(f"An error occurred: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    migrate()
