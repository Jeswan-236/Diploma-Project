import os
import json
import httpx
import time
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

# Load environment
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Constants
RAG_BUCKET_NAME = "rag-embeddings-bucket"
OPENROUTER_EMBEDDINGS_URL = "https://openrouter.ai/api/v1/embeddings"
OPENROUTER_EMBEDDING_MODEL = "openai/text-embedding-3-small"

# Initialize Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def chunk_transcript(text, chunk_size=800, overlap=150):
    if not text or not text.strip():
        return []
    text = text.strip()
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end >= len(text):
            chunks.append(text[start:].strip())
            break
        segment = text[start:end]
        para_break = segment.rfind('\n\n')
        if para_break > chunk_size * 0.3:
            end = start + para_break + 2
        else:
            sentence_break = max(segment.rfind('. '), segment.rfind('! '), segment.rfind('? '))
            if sentence_break > chunk_size * 0.3:
                end = start + sentence_break + 2
            else:
                word_break = segment.rfind(' ')
                if word_break > chunk_size * 0.3:
                    end = start + word_break + 1
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = max(start + 1, end - overlap)
    return chunks

def generate_embeddings(chunks):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": OPENROUTER_EMBEDDING_MODEL,
        "input": chunks
    }
    with httpx.Client(timeout=60.0) as client:
        response = client.post(OPENROUTER_EMBEDDINGS_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json().get("data", [])
        return [d.get("embedding", []) for d in data]

def main():
    print("Fetching videos for batch RAG processing...")
    res = supabase.table("ai_video_table").select("*").neq("status", "processed").execute()
    videos = res.data
    print(f"Found {len(videos)} videos to process.")

    for i, v in enumerate(videos):
        video_id = v['video_id']
        transcript = v.get('transcript_raw')
        
        if not transcript:
            print(f"[{i+1}/{len(videos)}] Skipping {video_id}: No transcript found.")
            continue

        print(f"[{i+1}/{len(videos)}] Processing {video_id}...")
        
        try:
            # 1. Chunk
            chunks = chunk_transcript(transcript)
            print(f"  - Split into {len(chunks)} chunks")
            
            # 2. Embed
            embeddings = generate_embeddings(chunks)
            print(f"  - Generated {len(embeddings)} embeddings")
            
            # 3. Assemble JSON
            paired = [{"chunk_index": idx, "text": text, "embedding": emb} for idx, (text, emb) in enumerate(zip(chunks, embeddings))]
            doc = {
                "video_id": video_id,
                "model": OPENROUTER_EMBEDDING_MODEL,
                "chunk_count": len(paired),
                "created_at": datetime.utcnow().isoformat(),
                "chunks": paired
            }
            
            # 4. Upload to Storage
            file_name = f"{video_id}_embeddings.json"
            supabase.storage.from_(RAG_BUCKET_NAME).upload(
                path=file_name,
                file=json.dumps(doc).encode("utf-8"),
                file_options={"content-type": "application/json", "upsert": "true"}
            )
            print(f"  - Uploaded to storage: {file_name}")
            
            # 5. Update Database
            file_url = supabase.storage.from_(RAG_BUCKET_NAME).get_public_url(file_name)
            if not isinstance(file_url, str): file_url = file_url.get("publicURL")
            
            supabase.table("ai_video_table").update({
                "bucket_file_name": file_name,
                "bucket_file_url": file_url,
                "chunk_count": len(paired),
                "status": "processed",
                "processed_at": datetime.utcnow().isoformat()
            }).eq("video_id", video_id).execute()
            
            print(f"  - Database updated successfully.")
            
            # Rate limit courtesy
            time.sleep(2)
            
        except Exception as e:
            print(f"  [ERROR] Failed to process {video_id}: {e}")

if __name__ == "__main__":
    if not OPENROUTER_API_KEY:
        print("Error: OPENROUTER_API_KEY not found in .env")
    else:
        main()
