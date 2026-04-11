-- =======================================================================
-- RAG Pipeline: ai_video_table
-- This table serves as the index linking video IDs to their
-- RAG embedding files stored in Supabase Storage.
-- =======================================================================

CREATE TABLE IF NOT EXISTS ai_video_table (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    video_id TEXT NOT NULL UNIQUE,
    bucket_file_name TEXT NOT NULL,
    bucket_file_url TEXT,
    chunk_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending',
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast lookups by video_id
CREATE INDEX IF NOT EXISTS idx_ai_video_table_video_id ON ai_video_table(video_id);

-- Index for filtering by status
CREATE INDEX IF NOT EXISTS idx_ai_video_table_status ON ai_video_table(status);

-- Enable Row Level Security (optional, recommended)
ALTER TABLE ai_video_table ENABLE ROW LEVEL SECURITY;

-- Allow authenticated users to read
CREATE POLICY "Allow authenticated read" ON ai_video_table
    FOR SELECT
    USING (auth.role() = 'authenticated' OR auth.role() = 'anon');

-- Allow service role full access (for backend inserts/updates)
CREATE POLICY "Allow service role full access" ON ai_video_table
    FOR ALL
    USING (auth.role() = 'service_role');

-- =======================================================================
-- NOTE: You must also create the Supabase Storage bucket manually:
--
-- 1. Go to Supabase Dashboard > Storage
-- 2. Click "New Bucket"
-- 3. Name: "rag-embeddings-bucket"
-- 4. Set Public = true (so the practice lab can fetch embeddings)
-- 5. Click "Create Bucket"
--
-- Alternatively, use the Supabase CLI:
--   supabase storage create rag-embeddings-bucket --public
-- =======================================================================
