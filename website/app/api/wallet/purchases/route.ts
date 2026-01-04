import { createClient } from '@/lib/supabase/server'
import { NextResponse } from 'next/server'

export async function GET() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const { data: purchases, error } = await supabase
    .from('purchases')
    .select('*')
    .eq('user_id', user.id)
    .order('created_at', { ascending: false })
    .limit(20)

  if (error) {
    console.error('Failed to fetch purchases:', error)
    return NextResponse.json({ purchases: [] })
  }

  return NextResponse.json({
    purchases: purchases.map((p) => ({
      id: p.id,
      amount: p.amount,
      merchant: p.merchant,
      category: p.category,
      description: p.description,
      status: p.status,
      createdAt: p.created_at,
    })),
  })
}
