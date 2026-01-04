import { createClient } from '@/lib/supabase/server'
import { NextResponse } from 'next/server'

export async function GET() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  let { data: wallet } = await supabase
    .from('wallets')
    .select('*')
    .eq('user_id', user.id)
    .single()

  if (!wallet) {
    const { data: newWallet, error } = await supabase
      .from('wallets')
      .insert({ user_id: user.id, balance: 100 })
      .select()
      .single()

    if (error) {
      console.error('Failed to create wallet:', error)
      return NextResponse.json({ balance: 100, spent: 0, currency: 'USD' })
    }
    wallet = newWallet
  }

  const { data: purchases } = await supabase
    .from('purchases')
    .select('amount')
    .eq('user_id', user.id)
    .eq('status', 'completed')

  const spent = purchases?.reduce((sum, p) => sum + (p.amount || 0), 0) || 0

  return NextResponse.json({
    balance: wallet.balance,
    spent,
    currency: 'USD',
  })
}
