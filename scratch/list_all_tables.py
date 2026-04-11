
import os
import requests
from dotenv import load_dotenv

# Path to .env from scratch/check_db.py
env_path = os.path.join(os.path.dirname(__file__), "../backend/.env")
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Missing credentials")
    exit(1)

# Query PostgREST directly for technical info
try:
    url = f"{SUPABASE_URL}/rest/v1/"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    # Fetching the OpenAPI spec which lists all tables
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        spec = response.json()
        definitions = spec.get("definitions", {})
        print("Available tables in Supabase:")
        for table in definitions.keys():
            print(f" - {table}")
    else:
        print(f"Failed to fetch spec: {response.status_code} {response.text}")

except Exception as e:
    print(f"Error: {e}")
