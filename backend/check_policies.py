import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Check existing policies
    cursor.execute("""
        SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
        FROM pg_policies
        WHERE tablename = 'ai_video_table';
    """)

    policies = cursor.fetchall()
    print("Current RLS policies on ai_video_table:")
    for policy in policies:
        print(f"  - {policy[2]}: {policy[5]} for roles {policy[4]}")

    if not policies:
        print("  No policies found")

    # Try to create the policy again
    print("\nAttempting to create anon access policy...")
    cursor.execute("""
        DROP POLICY IF EXISTS "Allow anon full access" ON ai_video_table;
        CREATE POLICY "Allow anon full access" ON ai_video_table
        FOR ALL
        USING (auth.role() = 'anon');
    """)

    conn.commit()
    print("✅ Policy created successfully")

except Exception as e:
    print(f"❌ Error: {e}")

finally:
    if 'conn' in locals():
        conn.close()