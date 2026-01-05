import { createClient } from '@/lib/supabase/server'
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url)
  const code = searchParams.get('code')
  const next = searchParams.get('next') ?? '/chat'

  if (code) {
    try {
      const supabase = await createClient()
      const { error } = await supabase.auth.exchangeCodeForSession(code)

      if (!error) {
        return NextResponse.redirect(`${origin}${next}`)
      }

      console.error('Auth code exchange error:', error.message)
      return NextResponse.redirect(`${origin}/login?error=${encodeURIComponent(error.message)}`)
    } catch (err) {
      console.error('Auth callback exception:', err)
      return NextResponse.redirect(`${origin}/login?error=server_error`)
    }
  }

  // No code provided
  return NextResponse.redirect(`${origin}/login?error=no_code`)
}
