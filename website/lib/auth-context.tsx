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

    supabase.auth.getUser().then(({ data }: { data: { user: { id: string; email?: string } | null } }) => {
      if (data?.user) setUser({ id: data.user.id, email: data.user.email || '' })
      setLoading(false)
    })

    const { data: { subscription } } = supabase.auth.onAuthStateChange((event: string, session: { user?: { id: string; email?: string } } | null) => {
      if (event === 'SIGNED_IN' && session?.user) {
        setUser({ id: session.user.id, email: session.user.email || '' })
        if (window.location.hash) window.history.replaceState(null, '', window.location.pathname)
      } else if (event === 'SIGNED_OUT') {
        setUser(null)
      }
      setLoading(false)
    })

    return () => subscription.unsubscribe()
  }, [])

  const signOut = async () => {
    await createClient().auth.signOut()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, signOut }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
