import { createClient } from '@/lib/supabase/server'
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const code = searchParams.get('code')
  const state = searchParams.get('state')
  const error = searchParams.get('error')

  if (error) {
    return NextResponse.redirect(new URL('/settings/connections?error=' + error, request.url))
  }

  if (!code || !state) {
    return NextResponse.redirect(new URL('/settings/connections?error=missing_params', request.url))
  }

  try {
    const stateData = JSON.parse(Buffer.from(state, 'base64').toString())
    const supabase = await createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user || user.id !== stateData.userId) {
      return NextResponse.redirect(new URL('/settings/connections?error=invalid_state', request.url))
    }

    const tokenResponse = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        code,
        client_id: process.env.GOOGLE_CLIENT_ID!,
        client_secret: process.env.GOOGLE_CLIENT_SECRET!,
        redirect_uri: process.env.NEXT_PUBLIC_APP_URL + '/api/oauth/google/callback',
        grant_type: 'authorization_code',
      }),
    })

    if (!tokenResponse.ok) {
      console.error('Token exchange failed:', await tokenResponse.text())
      return NextResponse.redirect(new URL('/settings/connections?error=token_exchange_failed', request.url))
    }

    const tokens = await tokenResponse.json()

    const userInfoResponse = await fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
      headers: { Authorization: `Bearer ${tokens.access_token}` },
    })
    const userInfo = await userInfoResponse.json()

    const { error: upsertError } = await supabase
      .from('oauth_connections')
      .upsert({
        user_id: user.id,
        provider: 'google',
        access_token_encrypted: tokens.access_token,
        refresh_token_encrypted: tokens.refresh_token,
        token_expires_at: new Date(Date.now() + tokens.expires_in * 1000).toISOString(),
        scopes: ['calendar', 'email'],
        status: 'valid',
        email: userInfo.email,
        connected_at: new Date().toISOString(),
      }, {
        onConflict: 'user_id,provider',
      })

    if (upsertError) {
      console.error('Failed to store tokens:', upsertError)
      return NextResponse.redirect(new URL('/settings/connections?error=storage_failed', request.url))
    }

    return NextResponse.redirect(new URL('/settings/connections?success=google', request.url))
  } catch (err) {
    console.error('OAuth callback error:', err)
    return NextResponse.redirect(new URL('/settings/connections?error=unknown', request.url))
  }
}
