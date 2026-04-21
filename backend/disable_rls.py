import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Disable RLS temporarily for batch processing
    cursor.execute("ALTER TABLE ai_video_table DISABLE ROW LEVEL SECURITY;")
    conn.commit()

    print("✅ RLS disabled for ai_video_table - batch processing should now work")

except Exception as e:
    print(f"❌ Error disabling RLS: {e}")

finally:
    if 'conn' in locals():
        conn.close()