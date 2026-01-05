-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Semantic memories table
CREATE TABLE IF NOT EXISTS semantic_memories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,
  channel TEXT NOT NULL,
  type TEXT NOT NULL CHECK (type IN ('fact', 'preference', 'event', 'context')),
  content TEXT NOT NULL,
  embedding vector(768), -- Gemini text-embedding-004 outputs 768 dimensions
  importance INTEGER NOT NULL DEFAULT 5 CHECK (importance >= 1 AND importance <= 10),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_accessed_at TIMESTAMPTZ DEFAULT NOW(),
  access_count INTEGER DEFAULT 0,

  -- Indexes for common queries
  CONSTRAINT unique_user_memory UNIQUE (user_id, channel, content)
);

-- Index for vector similarity search
CREATE INDEX IF NOT EXISTS semantic_memories_embedding_idx
ON semantic_memories
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Index for user/channel lookups
CREATE INDEX IF NOT EXISTS semantic_memories_user_channel_idx
ON semantic_memories (user_id, channel);

-- Index for importance-based queries
CREATE INDEX IF NOT EXISTS semantic_memories_importance_idx
ON semantic_memories (importance DESC);

-- Function to search memories by vector similarity
CREATE OR REPLACE FUNCTION search_memories(
  query_embedding vector(768),
  match_user_id TEXT,
  match_channel TEXT,
  match_threshold FLOAT DEFAULT 0.7,
  match_count INT DEFAULT 5
)
RETURNS TABLE (
  id UUID,
  user_id TEXT,
  channel TEXT,
  type TEXT,
  content TEXT,
  importance INTEGER,
  created_at TIMESTAMPTZ,
  last_accessed_at TIMESTAMPTZ,
  access_count INTEGER,
  similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    sm.id,
    sm.user_id,
    sm.channel,
    sm.type,
    sm.content,
    sm.importance,
    sm.created_at,
    sm.last_accessed_at,
    sm.access_count,
    1 - (sm.embedding <=> query_embedding) AS similarity
  FROM semantic_memories sm
  WHERE sm.user_id = match_user_id
    AND sm.channel = match_channel
    AND 1 - (sm.embedding <=> query_embedding) > match_threshold
  ORDER BY sm.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- Function to increment access count (for use in updates)
CREATE OR REPLACE FUNCTION increment_access_count()
RETURNS INTEGER
LANGUAGE sql
AS $$
  SELECT access_count + 1 FROM semantic_memories WHERE id = id;
$$;

-- RLS policies (optional but recommended)
ALTER TABLE semantic_memories ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their own memories via service role
-- (Since we use service role key, this is mainly for documentation)
CREATE POLICY "Service role full access"
ON semantic_memories
FOR ALL
USING (true)
WITH CHECK (true);
