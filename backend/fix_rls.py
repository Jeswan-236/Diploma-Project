import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Add RLS policy for anon role
    cursor.execute("""
        CREATE POLICY "Allow anon full access" ON ai_video_table
        FOR ALL
        USING (auth.role() = 'anon');
    """)

    conn.commit()
    print("✅ RLS policy updated successfully - anon role now has full access to ai_video_table")

except Exception as e:
    print(f"❌ Error updating RLS policy: {e}")
    print("You may need to update this manually in Supabase dashboard:")
    print("1. Go to Table Editor > ai_video_table")
    print("2. Go to RLS Policies")
    print("3. Add new policy: Allow anon full access, FOR ALL, USING (auth.role() = 'anon')")

finally:
    if 'conn' in locals():
        conn.close()