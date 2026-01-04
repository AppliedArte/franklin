import { AGENT_PROMPTS, classifyIntent } from '@/src/agents'

export const runtime = 'edge'

export async function POST(req: Request) {
  const { messages } = await req.json()

  // Get the last user message to classify intent
  const lastMessage = messages[messages.length - 1]?.content || ''
  const agentType = classifyIntent(lastMessage)

  // Build messages with system prompt
  const apiMessages = [
    { role: 'system', content: AGENT_PROMPTS[agentType] },
    ...messages.map((m: { role: string; content: string }) => ({
      role: m.role,
      content: m.content,
    })),
  ]

  // Call Z.AI with streaming
  const response = await fetch('https://api.z.ai/api/coding/paas/v4/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.Z_AI_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'GLM-4.7',
      messages: apiMessages,
      max_tokens: 1000,
      temperature: 0.7,
      stream: true,
    }),
  })

  if (!response.ok) {
    const error = await response.text()
    console.error('Z.AI error:', error)
    return new Response(JSON.stringify({ error: 'Failed to get response' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    })
  }

  // Transform Z.AI SSE stream to AI SDK compatible format
  const encoder = new TextEncoder()
  const decoder = new TextDecoder()

  const transformStream = new TransformStream({
    async transform(chunk, controller) {
      const text = decoder.decode(chunk)
      const lines = text.split('\n').filter(line => line.startsWith('data: '))

      for (const line of lines) {
        const data = line.slice(6).trim()
        if (data === '[DONE]') {
          controller.enqueue(encoder.encode('0:""\n'))
          continue
        }

        try {
          const parsed = JSON.parse(data)
          const content = parsed.choices?.[0]?.delta?.content
          if (content) {
            // AI SDK text stream format: 0:"text content"
            const escaped = JSON.stringify(content)
            controller.enqueue(encoder.encode(`0:${escaped}\n`))
          }
        } catch {
          // Skip malformed JSON
        }
      }
    },
  })

  return new Response(response.body?.pipeThrough(transformStream), {
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'X-Vercel-AI-Data-Stream': 'v1',
    },
  })
}
