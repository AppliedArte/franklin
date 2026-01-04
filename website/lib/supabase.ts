import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

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
