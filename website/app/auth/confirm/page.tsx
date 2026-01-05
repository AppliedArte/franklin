'use client'

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import { Loader2 } from 'lucide-react'

export default function AuthConfirmPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const exchangeCode = async () => {
      const code = searchParams.get('code')
      const next = searchParams.get('next') || '/chat'

      if (!code) {
        router.push('/login?error=no_code')
        return
      }

      try {
        const supabase = createClient()
        const { error } = await supabase.auth.exchangeCodeForSession(code)

        if (error) {
          console.error('Auth error:', error.message)
          setError(error.message)
          setTimeout(() => {
            router.push(`/login?error=${encodeURIComponent(error.message)}`)
          }, 2000)
          return
        }

        // Success - redirect to destination
        router.push(next)
      } catch (err) {
        console.error('Auth exception:', err)
        setError('Something went wrong')
        setTimeout(() => {
          router.push('/login?error=auth_failed')
        }, 2000)
      }
    }

    exchangeCode()
  }, [searchParams, router])

  return (
    <div className="min-h-screen bg-ivory-100 flex items-center justify-center">
      <div className="text-center space-y-4">
        {error ? (
          <>
            <div className="text-red-600 font-sans">{error}</div>
            <p className="text-silver-600 text-sm">Redirecting to login...</p>
          </>
        ) : (
          <>
            <Loader2 className="w-8 h-8 animate-spin text-gold-600 mx-auto" />
            <p className="text-silver-600 font-sans">Signing you in...</p>
          </>
        )}
      </div>
    </div>
  )
}
