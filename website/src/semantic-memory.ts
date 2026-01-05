/**
 * Semantic Memory Module
 * Uses Supabase pgvector + Gemini embeddings for intelligent memory retrieval
 */

import { createClient, SupabaseClient } from '@supabase/supabase-js'

let supabaseInstance: SupabaseClient | null = null

function getSupabase(): SupabaseClient {
  if (!supabaseInstance) {
    const supabaseUrl = process.env.SUPABASE_URL
    const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY

    if (!supabaseUrl || !supabaseServiceKey) {
      throw new Error('Missing Supabase environment variables')
    }

    supabaseInstance = createClient(supabaseUrl, supabaseServiceKey)
  }
  return supabaseInstance
}

// Memory types for categorization
export type MemoryType = 'fact' | 'preference' | 'event' | 'context'

export interface Memory {
  id?: string
  userId: string
  channel: string
  type: MemoryType
  content: string
  embedding?: number[]
  importance: number // 1-10 scale
  createdAt?: string
  lastAccessedAt?: string
  accessCount?: number
}

export interface SemanticSearchResult {
  memory: Memory
  similarity: number
}

// Generate embedding using Gemini
async function generateEmbedding(text: string): Promise<number[]> {
  const apiKey = process.env.GEMINI_API_KEY
  if (!apiKey) {
    throw new Error('Missing GEMINI_API_KEY')
  }

  const response = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key=${apiKey}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'models/text-embedding-004',
        content: { parts: [{ text }] },
      }),
    }
  )

  if (!response.ok) {
    const error = await response.text()
    console.error('Gemini embedding error:', error)
    throw new Error('Failed to generate embedding')
  }

  const data = await response.json()
  return data.embedding.values
}

// Store a memory with its embedding
export async function storeMemory(memory: Omit<Memory, 'embedding'>): Promise<string | null> {
  try {
    const embedding = await generateEmbedding(memory.content)

    const { data, error } = await getSupabase()
      .from('semantic_memories')
      .insert({
        user_id: memory.userId,
        channel: memory.channel,
        type: memory.type,
        content: memory.content,
        embedding: embedding,
        importance: memory.importance,
      })
      .select('id')
      .single()

    if (error) {
      console.error('Error storing memory:', error)
      return null
    }

    return data.id
  } catch (err) {
    console.error('Failed to store memory:', err)
    return null
  }
}

// Search memories by semantic similarity
export async function searchMemories(
  userId: string,
  channel: string,
  query: string,
  limit: number = 5,
  minSimilarity: number = 0.7
): Promise<SemanticSearchResult[]> {
  try {
    const queryEmbedding = await generateEmbedding(query)

    const { data, error } = await getSupabase().rpc('search_memories', {
      query_embedding: queryEmbedding,
      match_user_id: userId,
      match_channel: channel,
      match_threshold: minSimilarity,
      match_count: limit,
    })

    if (error) {
      console.error('Error searching memories:', error)
      return []
    }

    // Update access counts for retrieved memories
    if (data && data.length > 0) {
      const ids = data.map((m: any) => m.id)
      await getSupabase()
        .from('semantic_memories')
        .update({
          last_accessed_at: new Date().toISOString(),
          access_count: getSupabase().rpc('increment_access_count'),
        })
        .in('id', ids)
    }

    return (data || []).map((row: any) => ({
      memory: {
        id: row.id,
        userId: row.user_id,
        channel: row.channel,
        type: row.type,
        content: row.content,
        importance: row.importance,
        createdAt: row.created_at,
        lastAccessedAt: row.last_accessed_at,
        accessCount: row.access_count,
      },
      similarity: row.similarity,
    }))
  } catch (err) {
    console.error('Failed to search memories:', err)
    return []
  }
}

// Get all memories for a user (no semantic search)
export async function getAllMemories(
  userId: string,
  channel: string,
  type?: MemoryType
): Promise<Memory[]> {
  let query = getSupabase()
    .from('semantic_memories')
    .select('*')
    .eq('user_id', userId)
    .eq('channel', channel)
    .order('importance', { ascending: false })

  if (type) {
    query = query.eq('type', type)
  }

  const { data, error } = await query

  if (error) {
    console.error('Error fetching memories:', error)
    return []
  }

  return (data || []).map((row) => ({
    id: row.id,
    userId: row.user_id,
    channel: row.channel,
    type: row.type,
    content: row.content,
    importance: row.importance,
    createdAt: row.created_at,
    lastAccessedAt: row.last_accessed_at,
    accessCount: row.access_count,
  }))
}

// Delete a specific memory
export async function deleteMemory(memoryId: string): Promise<boolean> {
  const { error } = await getSupabase()
    .from('semantic_memories')
    .delete()
    .eq('id', memoryId)

  if (error) {
    console.error('Error deleting memory:', error)
    return false
  }

  return true
}

// Extract memories from a conversation using LLM
export async function extractMemoriesFromConversation(
  userId: string,
  channel: string,
  userMessage: string,
  assistantResponse: string
): Promise<void> {
  // Use Gemini to extract important facts/preferences
  const apiKey = process.env.GEMINI_API_KEY
  if (!apiKey) return

  const prompt = `Analyze this conversation and extract any important facts, preferences, or events worth remembering about the user. Return JSON array only, no markdown.

User message: "${userMessage}"
Assistant response: "${assistantResponse}"

Return format:
[
  {"type": "fact|preference|event", "content": "extracted memory", "importance": 1-10}
]

Rules:
- Only extract genuinely useful information
- Importance 1-3: trivial, 4-6: moderately useful, 7-10: very important
- Return empty array [] if nothing worth remembering
- Keep content concise (under 100 chars)
- Types: fact (about user), preference (likes/dislikes), event (something that happened)`

  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: {
            temperature: 0.1,
            maxOutputTokens: 500,
          },
        }),
      }
    )

    if (!response.ok) return

    const data = await response.json()
    const text = data.candidates?.[0]?.content?.parts?.[0]?.text || '[]'

    // Parse JSON from response
    const jsonMatch = text.match(/\[[\s\S]*\]/)
    if (!jsonMatch) return

    const memories = JSON.parse(jsonMatch[0])

    // Store each extracted memory
    for (const mem of memories) {
      if (mem.content && mem.type && mem.importance >= 4) {
        // Only store if importance >= 4
        await storeMemory({
          userId,
          channel,
          type: mem.type,
          content: mem.content,
          importance: mem.importance,
        })
      }
    }
  } catch (err) {
    console.error('Failed to extract memories:', err)
  }
}

// Build context from semantic memories for a query
export async function buildSemanticContext(
  userId: string,
  channel: string,
  currentQuery: string
): Promise<string> {
  const results = await searchMemories(userId, channel, currentQuery, 5, 0.65)

  if (results.length === 0) return ''

  let context = '\n\nRELEVANT MEMORIES:\n'
  for (const { memory, similarity } of results) {
    const typeLabel = memory.type.toUpperCase()
    context += `- [${typeLabel}] ${memory.content}\n`
  }

  return context
}

// Decay old, unused memories (run periodically)
export async function decayMemories(): Promise<number> {
  const thirtyDaysAgo = new Date()
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)

  // Delete low-importance memories that haven't been accessed in 30 days
  const { data, error } = await getSupabase()
    .from('semantic_memories')
    .delete()
    .lt('importance', 5)
    .lt('last_accessed_at', thirtyDaysAgo.toISOString())
    .select('id')

  if (error) {
    console.error('Error decaying memories:', error)
    return 0
  }

  return data?.length || 0
}
