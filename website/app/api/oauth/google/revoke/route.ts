import { createClient } from '@/lib/supabase/server'
import { NextResponse } from 'next/server'

export async function DELETE() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const { data: connection } = await supabase
    .from('oauth_connections')
    .select('access_token_encrypted')
    .eq('user_id', user.id)
    .eq('provider', 'google')
    .single()

  if (connection?.access_token_encrypted) {
    try {
      await fetch(`https://oauth2.googleapis.com/revoke?token=${connection.access_token_encrypted}`, {
        method: 'POST',
      })
    } catch (err) {
      console.error('Failed to revoke Google token:', err)
    }
  }

  const { error } = await supabase
    .from('oauth_connections')
    .delete()
    .eq('user_id', user.id)
    .eq('provider', 'google')

  if (error) {
    console.error('Failed to delete connection:', error)
    return NextResponse.json({ error: 'Failed to disconnect' }, { status: 500 })
  }

  return NextResponse.json({ success: true })
}
