import os
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client

def main():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")
    supabase = create_client(url, key)
    
    bucket_name = 'rag-embeddings-bucket'
    
    print(f"Attempting to create bucket: {bucket_name}...")
    try:
        # Check if it exists first
        buckets = supabase.storage.list_buckets()
        if any(b.name == bucket_name for b in buckets):
            print(f"Bucket '{bucket_name}' already exists.")
            return

        supabase.storage.create_bucket(bucket_name, options={'public': True})
        print(f"Bucket '{bucket_name}' created successfully.")
    except Exception as e:
        print(f"Error creating bucket: {e}")

if __name__ == "__main__":
    main()
