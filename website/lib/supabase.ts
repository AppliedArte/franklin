import { createClient, SupabaseClient } from '@supabase/supabase-js'

let supabaseInstance: SupabaseClient | null = null

export function getSupabase(): SupabaseClient {
  if (!supabaseInstance) {
    const supabaseUrl = process.env.SUPABASE_URL
    const supabaseAnonKey = process.env.SUPABASE_ANON_KEY

    if (!supabaseUrl || !supabaseAnonKey) {
      throw new Error('Missing Supabase environment variables')
    }

    supabaseInstance = createClient(supabaseUrl, supabaseAnonKey)
  }
  return supabaseInstance
}

// Backwards compatibility - lazy getter
export const supabase = new Proxy({} as SupabaseClient, {
  get(_, prop) {
    return (getSupabase() as any)[prop]
  }
})

export type Lead = {
  id?: string
  name: string
  phone: string
  email: string
  fund_name: string
  linkedin: string
  twitter?: string
  user_type: 'investor' | 'founder' | 'curious'
  created_at?: string
}
