-- Conversation Memory Table
-- Stores all messages for conversation history
CREATE TABLE IF NOT EXISTS conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,           -- Channel-specific user ID (e.g., Telegram chat ID)
  channel TEXT NOT NULL,           -- 'telegram', 'whatsapp', 'voice', 'web'
  role TEXT NOT NULL,              -- 'user' or 'assistant'
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast retrieval of recent messages
CREATE INDEX IF NOT EXISTS idx_conversations_user_channel
ON conversations(user_id, channel, created_at DESC);

-- User Profiles Table
-- Stores long-term memory: preferences, facts, profile data
CREATE TABLE IF NOT EXISTS user_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  channel_user_id TEXT NOT NULL,   -- Channel-specific user ID
  channel TEXT NOT NULL,           -- 'telegram', 'whatsapp', 'voice', 'web'
  name TEXT,
  email TEXT,
  phone TEXT,
  preferences JSONB DEFAULT '{}',  -- User preferences (risk tolerance, interests, etc.)
  facts TEXT[] DEFAULT '{}',       -- Extracted facts about the user
  user_type TEXT,                  -- 'investor', 'founder', etc.
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(channel_user_id, channel)
);

-- Index for fast profile lookup
CREATE INDEX IF NOT EXISTS idx_user_profiles_channel_user
ON user_profiles(channel_user_id, channel);

-- Optional: Add RLS policies if needed
-- ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
