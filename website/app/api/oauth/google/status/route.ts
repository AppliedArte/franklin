import { createClient } from '@/lib/supabase/server'
import { NextResponse } from 'next/server'

export async function GET() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const { data: connections, error } = await supabase
    .from('oauth_connections')
    .select('provider, status, scopes, connected_at, email')
    .eq('user_id', user.id)

  if (error) {
    console.error('Failed to fetch connections:', error)
    return NextResponse.json({ connections: {} })
  }

  const connectionsMap = (connections || []).reduce((acc, conn) => ({
    ...acc,
    [conn.provider]: {
      status: conn.status,
      scopes: conn.scopes,
      connectedAt: conn.connected_at,
      email: conn.email,
    }
  }), {})

  return NextResponse.json({ connections: connectionsMap })
}
