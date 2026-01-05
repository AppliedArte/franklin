'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { createClient } from '@/lib/supabase/client'

type User = {
  id: string
  email: string
} | null

type AuthContextType = {
  user: User
  loading: boolean
  signOut: () => Promise<void>
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  signOut: async () => {},
})

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const supabase = createClient()

    // Check current user
    supabase.auth.getUser().then((result: { data: { user: { id: string; email?: string } | null } }) => {
      if (result.data?.user) {
        setUser({ id: result.data.user.id, email: result.data.user.email || '' })
      }
      setLoading(false)
    })

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event: string, session: { user?: { id: string; email?: string } } | null) => {
      if (event === 'SIGNED_IN' && session?.user) {
        setUser({ id: session.user.id, email: session.user.email || '' })
        // Clean up URL hash after successful auth
        if (typeof window !== 'undefined' && window.location.hash) {
          window.history.replaceState(null, '', window.location.pathname)
        }
      } else if (event === 'SIGNED_OUT') {
        setUser(null)
      }
      setLoading(false)
    })

    return () => subscription.unsubscribe()
  }, [])

  const signOut = async () => {
    const supabase = createClient()
    await supabase.auth.signOut()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, signOut }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
