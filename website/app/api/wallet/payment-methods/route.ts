import { createClient } from '@/lib/supabase/server'
import { NextResponse } from 'next/server'
import Stripe from 'stripe'

const getStripe = () => new Stripe(process.env.STRIPE_SECRET_KEY!)

export async function GET() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const { data: methods, error } = await supabase
    .from('payment_methods')
    .select('*')
    .eq('user_id', user.id)
    .order('created_at', { ascending: false })

  if (error) {
    console.error('Failed to fetch payment methods:', error)
    return NextResponse.json({ methods: [] })
  }

  return NextResponse.json({
    methods: methods.map((m) => ({
      id: m.id,
      brand: m.card_brand,
      last4: m.card_last4,
      expMonth: m.card_exp_month,
      expYear: m.card_exp_year,
      isDefault: m.is_default,
    })),
  })
}

export async function POST(request: Request) {
  const stripe = getStripe()
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const { paymentMethodId } = await request.json()

  try {
    const paymentMethod = await stripe.paymentMethods.retrieve(paymentMethodId)

    if (!paymentMethod.card) {
      return NextResponse.json({ error: 'Invalid payment method' }, { status: 400 })
    }

    const { count } = await supabase
      .from('payment_methods')
      .select('*', { count: 'exact', head: true })
      .eq('user_id', user.id)

    const { error } = await supabase.from('payment_methods').insert({
      user_id: user.id,
      stripe_payment_method_id: paymentMethodId,
      card_brand: paymentMethod.card.brand,
      card_last4: paymentMethod.card.last4,
      card_exp_month: paymentMethod.card.exp_month,
      card_exp_year: paymentMethod.card.exp_year,
      is_default: count === 0,
    })

    if (error) {
      console.error('Failed to save payment method:', error)
      return NextResponse.json({ error: 'Failed to save payment method' }, { status: 500 })
    }

    return NextResponse.json({ success: true })
  } catch (err) {
    console.error('Stripe error:', err)
    return NextResponse.json({ error: 'Failed to verify payment method' }, { status: 500 })
  }
}

export async function DELETE(request: Request) {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const { searchParams } = new URL(request.url)
  const methodId = searchParams.get('id')

  if (!methodId) {
    return NextResponse.json({ error: 'Missing method ID' }, { status: 400 })
  }

  const { error } = await supabase
    .from('payment_methods')
    .delete()
    .eq('id', methodId)
    .eq('user_id', user.id)

  if (error) {
    console.error('Failed to delete payment method:', error)
    return NextResponse.json({ error: 'Failed to delete' }, { status: 500 })
  }

  return NextResponse.json({ success: true })
}
