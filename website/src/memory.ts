import { createClient, SupabaseClient } from '@supabase/supabase-js'
import { buildSemanticContext, extractMemoriesFromConversation } from './semantic-memory'

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

export interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: string
}

export interface UserContext {
  userId: string
  userName: string
  channel: 'telegram' | 'whatsapp' | 'voice' | 'web'
  preferences?: Record<string, any>
  facts?: string[]
}

// Get recent conversation history for a user
export async function getConversationHistory(
  userId: string,
  channel: string,
  limit: number = 10
): Promise<Message[]> {
  const { data, error } = await getSupabase()
    .from('franklin_messages')
    .select('role, content, created_at')
    .eq('user_id', userId)
    .eq('channel', channel)
    .order('created_at', { ascending: false })
    .limit(limit)

  if (error) {
    console.error('Error fetching conversation history:', error)
    return []
  }

  // Reverse to get chronological order
  return (data || []).reverse().map(msg => ({
    role: msg.role as 'user' | 'assistant',
    content: msg.content,
    timestamp: msg.created_at,
  }))
}

// Save a message to conversation history
export async function saveMessage(
  userId: string,
  channel: string,
  role: 'user' | 'assistant',
  content: string
): Promise<void> {
  const { error } = await getSupabase().from('conversations').insert({
    user_id: userId,
    channel,
    role,
    content,
  })

  if (error) {
    console.error('Error saving message:', error)
  }
}

// Get or create user profile
export async function getUserProfile(userId: string, channel: string, userName?: string): Promise<UserContext> {
  const { data, error } = await getSupabase()
    .from('franklin_profiles')
    .select('*')
    .eq('channel_user_id', userId)
    .eq('channel', channel)
    .single()

  if (data) {
    return {
      userId: data.channel_user_id,
      userName: data.name || userName || 'friend',
      channel: data.channel,
      preferences: data.preferences || {},
      facts: data.facts || [],
    }
  }

  // Create new profile
  if (userName) {
    await getSupabase().from('user_profiles').insert({
      channel_user_id: userId,
      channel,
      name: userName,
      preferences: {},
      facts: [],
    })
  }

  return {
    userId,
    userName: userName || 'friend',
    channel: channel as any,
    preferences: {},
    facts: [],
  }
}

// Update user preferences (long-term memory)
export async function updateUserPreferences(
  userId: string,
  channel: string,
  preferences: Record<string, any>
): Promise<void> {
  const { error } = await getSupabase()
    .from('franklin_profiles')
    .update({ preferences, updated_at: new Date().toISOString() })
    .eq('channel_user_id', userId)
    .eq('channel', channel)

  if (error) {
    console.error('Error updating preferences:', error)
  }
}

// Add a fact to user's long-term memory
export async function addUserFact(
  userId: string,
  channel: string,
  fact: string
): Promise<void> {
  const { data } = await getSupabase()
    .from('franklin_profiles')
    .select('facts')
    .eq('channel_user_id', userId)
    .eq('channel', channel)
    .single()

  const facts = data?.facts || []
  if (!facts.includes(fact)) {
    facts.push(fact)
    await getSupabase()
      .from('franklin_profiles')
      .update({ facts, updated_at: new Date().toISOString() })
      .eq('channel_user_id', userId)
      .eq('channel', channel)
  }
}

// Build context string from user profile and history
export function buildContextPrompt(
  userContext: UserContext,
  history: Message[]
): string {
  let context = ''

  // Add user facts if any
  if (userContext.facts && userContext.facts.length > 0) {
    context += `\n\nKNOWN FACTS ABOUT ${userContext.userName.toUpperCase()}:\n`
    context += userContext.facts.map(f => `- ${f}`).join('\n')
  }

  // Add preferences if any
  if (userContext.preferences && Object.keys(userContext.preferences).length > 0) {
    context += `\n\nUSER PREFERENCES:\n`
    for (const [key, value] of Object.entries(userContext.preferences)) {
      context += `- ${key}: ${value}\n`
    }
  }

  return context
}

// Build context with semantic memory search
export async function buildContextPromptWithSemanticMemory(
  userContext: UserContext,
  history: Message[],
  currentQuery: string
): Promise<string> {
  let context = buildContextPrompt(userContext, history)

  // Add semantically relevant memories
  const semanticContext = await buildSemanticContext(
    userContext.userId,
    userContext.channel,
    currentQuery
  )
  context += semanticContext

  return context
}

// Process conversation and extract memories (call after each exchange)
export async function processConversationMemory(
  userId: string,
  channel: string,
  userMessage: string,
  assistantResponse: string
): Promise<void> {
  await extractMemoriesFromConversation(userId, channel, userMessage, assistantResponse)
}

// Re-export semantic memory functions for convenience
export {
  storeMemory,
  searchMemories,
  getAllMemories,
  deleteMemory,
  decayMemories,
} from './semantic-memory'
