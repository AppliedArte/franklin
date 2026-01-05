import { createBrowserClient } from '@supabase/ssr'

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function createClient(): any {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL
  const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

  if (!url || !key) {
    // Return a mock client that does nothing - auth features disabled
    return {
      auth: {
        getUser: async () => ({ data: { user: null }, error: null }),
        signInWithOtp: async () => ({ data: null, error: { message: 'Auth not configured' } }),
        signOut: async () => ({ error: null }),
      }
    }
  }

  return createBrowserClient(url, key, {
    auth: {
      flowType: 'implicit',
    },
  })
}
