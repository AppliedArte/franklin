'use client'

import { useState, useEffect } from 'react'
import {
  Wallet,
  CreditCard,
  Plus,
  Loader2,
  Check,
  Clock,
  XCircle,
  AlertCircle,
  Settings,
  ShoppingBag
} from 'lucide-react'
import { loadStripe } from '@stripe/stripe-js'
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js'

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || '')

interface WalletData {
  balance: number
  spent: number
  currency: string
}

interface PaymentMethod {
  id: string
  brand: string
  last4: string
  expMonth: number
  expYear: number
  isDefault: boolean
}

interface Purchase {
  id: string
  amount: number
  merchant: string
  category: string
  status: string
  createdAt: string
}

interface SpendingRule {
  autoApproveUpTo: number
  requireConfirmationAbove: number
}

function AddCardForm({ onSuccess, onCancel }: { onSuccess: () => void; onCancel: () => void }) {
  const stripe = useStripe()
  const elements = useElements()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!stripe || !elements) return

    setLoading(true)
    setError('')

    try {
      // Get setup intent from server
      const intentRes = await fetch('/api/stripe/setup-intent', { method: 'POST' })
      const { clientSecret } = await intentRes.json()

      // Confirm setup
      const { error: stripeError, setupIntent } = await stripe.confirmCardSetup(clientSecret, {
        payment_method: {
          card: elements.getElement(CardElement)!,
        },
      })

      if (stripeError) {
        setError(stripeError.message || 'Failed to add card')
        return
      }

      // Save payment method to our database
      await fetch('/api/wallet/payment-methods', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ paymentMethodId: setupIntent?.payment_method }),
      })

      onSuccess()
    } catch (err) {
      setError('Failed to add card')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="p-4 border border-silver-300 rounded-xl bg-ivory-100">
        <CardElement
          options={{
            style: {
              base: {
                fontSize: '16px',
                color: '#495057',
                fontFamily: 'DM Sans, sans-serif',
                '::placeholder': { color: '#adb5bd' },
              },
            },
          }}
        />
      </div>
      {error && (
        <p className="text-red-600 text-sm font-sans">{error}</p>
      )}
      <div className="flex gap-3">
        <button
          type="submit"
          disabled={!stripe || loading}
          className="btn-primary flex-1 rounded-xl flex items-center justify-center gap-2"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
          Add Card
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-silver-600 hover:text-silver-800 font-sans"
        >
          Cancel
        </button>
      </div>
    </form>
  )
}

export default function WalletPage() {
  const [wallet, setWallet] = useState<WalletData | null>(null)
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([])
  const [purchases, setPurchases] = useState<Purchase[]>([])
  const [rules, setRules] = useState<SpendingRule[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddCard, setShowAddCard] = useState(false)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [walletRes, methodsRes, purchasesRes, rulesRes] = await Promise.all([
        fetch('/api/wallet/balance'),
        fetch('/api/wallet/payment-methods'),
        fetch('/api/wallet/purchases'),
        fetch('/api/wallet/rules'),
      ])

      if (walletRes.ok) setWallet(await walletRes.json())
      if (methodsRes.ok) setPaymentMethods((await methodsRes.json()).methods || [])
      if (purchasesRes.ok) setPurchases((await purchasesRes.json()).purchases || [])
      if (rulesRes.ok) setRules((await rulesRes.json()).rules || [])
    } catch (error) {
      console.error('Failed to fetch wallet data:', error)
    } finally {
      setLoading(false)
    }
  }

  const statusConfig = {
    completed: { icon: <Check className="w-4 h-4 text-green-600" />, color: 'bg-green-100 text-green-700' },
    pending: { icon: <Clock className="w-4 h-4 text-gold-600" />, color: 'bg-gold-100 text-gold-700' },
    failed: { icon: <XCircle className="w-4 h-4 text-red-600" />, color: 'bg-red-100 text-red-700' },
  }

  const getStatus = (status: string) =>
    statusConfig[status as keyof typeof statusConfig] ||
    { icon: <AlertCircle className="w-4 h-4 text-silver-400" />, color: 'bg-silver-100 text-silver-600' }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 text-silver-400 animate-spin" />
      </div>
    )
  }

  const balance = wallet?.balance ?? 100
  const spent = wallet?.spent ?? 0
  const spentPercent = (spent / balance) * 100

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="font-display text-2xl text-silver-800 mb-2">Franklin's Wallet</h2>
        <p className="text-silver-600 font-body">
          Franklin has a budget to make purchases on your behalf.
        </p>
      </div>

      {/* Balance Card */}
      <div className="bg-gradient-to-br from-silver-700 to-silver-900 rounded-2xl p-6 text-ivory-100">
        <div className="flex items-start justify-between mb-6">
          <div>
            <p className="text-silver-300 font-sans text-sm mb-1">Available Balance</p>
            <p className="font-display text-4xl">${(balance - spent).toFixed(2)}</p>
          </div>
          <div className="w-12 h-12 rounded-full bg-gold-400/20 flex items-center justify-center">
            <Wallet className="w-6 h-6 text-gold-400" />
          </div>
        </div>

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm font-sans">
            <span className="text-silver-300">Spent this month</span>
            <span className="text-silver-300">${spent.toFixed(2)} / ${balance.toFixed(2)}</span>
          </div>
          <div className="h-2 bg-silver-600 rounded-full overflow-hidden">
            <div
              className="h-full bg-gold-400 rounded-full transition-all"
              style={{ width: `${Math.min(spentPercent, 100)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Payment Methods */}
      <div className="bg-ivory-50 border border-silver-200 rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-display text-lg text-silver-800 flex items-center gap-2">
            <CreditCard className="w-5 h-5 text-gold-500" />
            Payment Methods
          </h3>
          {!showAddCard && (
            <button
              onClick={() => setShowAddCard(true)}
              className="text-sm font-sans text-gold-600 hover:text-gold-700 flex items-center gap-1"
            >
              <Plus className="w-4 h-4" />
              Add Card
            </button>
          )}
        </div>

        {showAddCard ? (
          <Elements stripe={stripePromise}>
            <AddCardForm
              onSuccess={() => {
                setShowAddCard(false)
                fetchData()
              }}
              onCancel={() => setShowAddCard(false)}
            />
          </Elements>
        ) : paymentMethods.length > 0 ? (
          <div className="space-y-3">
            {paymentMethods.map((method) => (
              <div
                key={method.id}
                className="flex items-center justify-between p-3 bg-ivory-100 rounded-xl"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-silver-200 flex items-center justify-center">
                    <CreditCard className="w-5 h-5 text-silver-600" />
                  </div>
                  <div>
                    <p className="font-sans text-silver-800">
                      {method.brand.charAt(0).toUpperCase() + method.brand.slice(1)} ****{method.last4}
                    </p>
                    <p className="text-xs text-silver-500 font-sans">
                      Expires {method.expMonth}/{method.expYear}
                    </p>
                  </div>
                </div>
                {method.isDefault && (
                  <span className="text-xs font-sans px-2 py-1 bg-gold-100 text-gold-700 rounded-full">
                    Default
                  </span>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-silver-500">
            <CreditCard className="w-12 h-12 mx-auto mb-3 text-silver-300" />
            <p className="font-sans">No payment methods added yet</p>
            <p className="text-sm mt-1">Add a card so Franklin can make purchases</p>
          </div>
        )}
      </div>

      {/* Spending Rules */}
      <div className="bg-ivory-50 border border-silver-200 rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-display text-lg text-silver-800 flex items-center gap-2">
            <Settings className="w-5 h-5 text-gold-500" />
            Spending Rules
          </h3>
        </div>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-ivory-100 rounded-xl">
              <p className="text-xs text-silver-500 font-sans uppercase tracking-wide mb-1">
                Auto-approve up to
              </p>
              <p className="font-display text-2xl text-silver-800">
                ${rules[0]?.autoApproveUpTo ?? 25}
              </p>
            </div>
            <div className="p-4 bg-ivory-100 rounded-xl">
              <p className="text-xs text-silver-500 font-sans uppercase tracking-wide mb-1">
                Confirm above
              </p>
              <p className="font-display text-2xl text-silver-800">
                ${rules[0]?.requireConfirmationAbove ?? 50}
              </p>
            </div>
          </div>

          <p className="text-sm text-silver-600 font-body">
            Franklin will automatically approve small purchases. For larger amounts,
            he'll ask for your confirmation via chat or WhatsApp.
          </p>
        </div>
      </div>

      {/* Purchase History */}
      <div className="bg-ivory-50 border border-silver-200 rounded-2xl p-6">
        <h3 className="font-display text-lg text-silver-800 flex items-center gap-2 mb-4">
          <ShoppingBag className="w-5 h-5 text-gold-500" />
          Recent Purchases
        </h3>

        {purchases.length > 0 ? (
          <div className="space-y-3">
            {purchases.map((purchase) => (
              <div
                key={purchase.id}
                className="flex items-center justify-between p-4 bg-ivory-100 rounded-xl"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-silver-200 flex items-center justify-center">
                    <ShoppingBag className="w-5 h-5 text-silver-600" />
                  </div>
                  <div>
                    <p className="font-sans text-silver-800">{purchase.merchant}</p>
                    <p className="text-xs text-silver-500 font-sans">
                      {purchase.category} • {new Date(purchase.createdAt).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-display text-silver-800">${purchase.amount.toFixed(2)}</p>
                  <span className={`inline-flex items-center gap-1 text-xs font-sans px-2 py-0.5 rounded-full ${getStatus(purchase.status).color}`}>
                    {getStatus(purchase.status).icon}
                    {purchase.status.charAt(0).toUpperCase() + purchase.status.slice(1)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-silver-500">
            <ShoppingBag className="w-12 h-12 mx-auto mb-3 text-silver-300" />
            <p className="font-sans">No purchases yet</p>
            <p className="text-sm mt-1">Franklin hasn't made any purchases on your behalf</p>
          </div>
        )}
      </div>
    </div>
  )
}
