'use client'

import { useState, useEffect } from 'react'
import { Calendar, Mail, CheckCircle, XCircle, Loader2, ExternalLink } from 'lucide-react'

interface Connection {
  status: 'connected' | 'disconnected' | 'expired'
  scopes: string[]
  connectedAt?: string
  email?: string
}

const integrations = [
  {
    id: 'google',
    name: 'Google',
    description: 'Connect your Google account for Calendar and Gmail access',
    icon: (
      <svg className="w-6 h-6" viewBox="0 0 24 24">
        <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
        <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
        <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
        <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
      </svg>
    ),
    scopes: [
      { id: 'calendar', name: 'Calendar', description: 'View and manage your calendar events' },
      { id: 'email', name: 'Gmail', description: 'Read and send emails on your behalf' },
    ],
  },
]

export default function ConnectionsPage() {
  const [connections, setConnections] = useState<Record<string, Connection>>({})
  const [loading, setLoading] = useState(true)
  const [connecting, setConnecting] = useState<string | null>(null)
  const [disconnecting, setDisconnecting] = useState<string | null>(null)

  useEffect(() => {
    fetchConnections()
  }, [])

  const fetchConnections = async () => {
    try {
      const response = await fetch('/api/oauth/google/status')
      if (response.ok) setConnections((await response.json()).connections || {})
    } catch (error) {
      console.error('Failed to fetch connections:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleConnect = async (provider: string) => {
    setConnecting(provider)
    try {
      const response = await fetch(`/api/oauth/${provider}/authorize`)
      const data = await response.json()
      if (data.url) {
        window.location.href = data.url
      }
    } catch (error) {
      console.error('Failed to start OAuth:', error)
      setConnecting(null)
    }
  }

  const handleDisconnect = async (provider: string) => {
    setDisconnecting(provider)
    try {
      await fetch(`/api/oauth/${provider}/revoke`, { method: 'DELETE' })
      setConnections((prev) => {
        const { [provider]: _, ...rest } = prev
        return rest
      })
    } catch (error) {
      console.error('Failed to disconnect:', error)
    } finally {
      setDisconnecting(null)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 text-silver-400 animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-display text-2xl text-silver-800 mb-2">Data Connections</h2>
        <p className="text-silver-600 font-body">
          Connect your accounts so Franklin can access your calendar and email.
        </p>
      </div>

      <div className="space-y-4">
        {integrations.map((integration) => {
          const connection = connections[integration.id]
          const isConnected = connection?.status === 'connected'
          const isConnecting = connecting === integration.id
          const isDisconnecting = disconnecting === integration.id

          return (
            <div
              key={integration.id}
              className="bg-ivory-50 border border-silver-200 rounded-2xl p-6 transition-all hover:border-silver-300"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-white border border-silver-200 flex items-center justify-center">
                    {integration.icon}
                  </div>
                  <div>
                    <h3 className="font-display text-lg text-silver-800">{integration.name}</h3>
                    <p className="text-sm text-silver-500 font-sans">{integration.description}</p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {isConnected ? (
                    <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-green-100 text-green-700 text-sm font-sans">
                      <CheckCircle className="w-4 h-4" />
                      Connected
                    </span>
                  ) : (
                    <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-silver-100 text-silver-600 text-sm font-sans">
                      <XCircle className="w-4 h-4" />
                      Not connected
                    </span>
                  )}
                </div>
              </div>

              {/* Scopes */}
              <div className="mb-4 pl-16">
                <p className="text-xs text-silver-500 font-sans uppercase tracking-wide mb-2">
                  Permissions
                </p>
                <div className="flex flex-wrap gap-2">
                  {integration.scopes.map((scope) => (
                    <div
                      key={scope.id}
                      className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm ${
                        isConnected
                          ? 'bg-gold-50 text-gold-700 border border-gold-200'
                          : 'bg-silver-50 text-silver-600 border border-silver-200'
                      }`}
                    >
                      {scope.id === 'calendar' ? (
                        <Calendar className="w-4 h-4" />
                      ) : (
                        <Mail className="w-4 h-4" />
                      )}
                      {scope.name}
                    </div>
                  ))}
                </div>
              </div>

              {/* Connected Info or Connect Button */}
              <div className="pl-16">
                {isConnected ? (
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-silver-500 font-sans">
                      {connection.email && (
                        <span>Connected as <strong>{connection.email}</strong></span>
                      )}
                      {connection.connectedAt && (
                        <span className="ml-2 text-silver-400">
                          since {new Date(connection.connectedAt).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                    <button
                      onClick={() => handleDisconnect(integration.id)}
                      disabled={isDisconnecting}
                      className="px-4 py-2 text-sm font-sans text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-all disabled:opacity-50"
                    >
                      {isDisconnecting ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        'Disconnect'
                      )}
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => handleConnect(integration.id)}
                    disabled={isConnecting}
                    className="btn-primary flex items-center gap-2 rounded-xl"
                  >
                    {isConnecting ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <>
                        Connect {integration.name}
                        <ExternalLink className="w-4 h-4" />
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Info Box */}
      <div className="bg-gold-50/50 border border-gold-200 rounded-xl p-4">
        <p className="text-sm text-gold-700 font-body">
          <strong className="font-sans">Privacy Note:</strong> Franklin only accesses data needed to help you.
          Your credentials are encrypted and you can disconnect at any time.
        </p>
      </div>
    </div>
  )
}
