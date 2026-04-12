import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

def analyze_schema():
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found in .env")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # Get all tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = [row[0] for row in cur.fetchall()]

        print("--- Database Schema Analysis ---")
        for table in tables:
            print(f"\nTable: {table}")
            cur.execute(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position;
            """, (table,))
            columns = cur.fetchall()
            for col in columns:
                print(f"  - {col[0]} ({col[1]}, nullable: {col[2]})")

        conn.close()

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    analyze_schema()
