import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url)
  const code = searchParams.get('code')
  const next = searchParams.get('next') ?? '/chat'

  if (code) {
    // Redirect to client-side page to exchange code (PKCE verifier is in browser cookies)
    return NextResponse.redirect(`${origin}/auth/confirm?code=${code}&next=${encodeURIComponent(next)}`)
  }

  return NextResponse.redirect(`${origin}/login?error=no_code`)
}
