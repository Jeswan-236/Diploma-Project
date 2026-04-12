import os
import psycopg2
from dotenv import load_dotenv
import json

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

def check_connectivity():
    results = {
        "database_connected": False,
        "tables_found": [],
        "error": None
    }
    
    if not DATABASE_URL:
        results["error"] = "DATABASE_URL not found in .env"
        print(json.dumps(results))
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Test 1: Identify all tables
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        results["tables_found"] = [row[0] for row in cur.fetchall()]
        results["database_connected"] = True
        
        conn.close()
    except Exception as e:
        results["error"] = str(e)

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    check_connectivity()
