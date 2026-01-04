import { createClient } from '@/lib/supabase/server'
import { NextResponse } from 'next/server'

const DEFAULT_RULES = [{
  category: null,
  autoApproveUpTo: 25,
  requireConfirmationAbove: 50,
  monthlyLimit: null,
}]

export async function GET() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const { data: rules, error } = await supabase
    .from('spending_rules')
    .select('*')
    .eq('user_id', user.id)

  if (error) {
    console.error('Failed to fetch spending rules:', error)
  }

  if (!rules?.length) {
    return NextResponse.json({ rules: DEFAULT_RULES })
  }

  return NextResponse.json({
    rules: rules.map((r) => ({
      category: r.category,
      autoApproveUpTo: r.auto_approve_up_to,
      requireConfirmationAbove: r.require_confirmation_above,
      monthlyLimit: r.monthly_limit,
    })),
  })
}

export async function POST(request: Request) {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const body = await request.json()
  const { category, autoApproveUpTo, requireConfirmationAbove, monthlyLimit } = body

  const { error } = await supabase
    .from('spending_rules')
    .upsert({
      user_id: user.id,
      category: category || null,
      auto_approve_up_to: autoApproveUpTo,
      require_confirmation_above: requireConfirmationAbove,
      monthly_limit: monthlyLimit,
    }, {
      onConflict: 'user_id,category',
    })

  if (error) {
    console.error('Failed to save spending rule:', error)
    return NextResponse.json({ error: 'Failed to save rule' }, { status: 500 })
  }

  return NextResponse.json({ success: true })
}
