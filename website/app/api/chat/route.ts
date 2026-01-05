import { AGENT_PROMPTS, classifyIntent } from '@/src/agents'

export const runtime = 'edge'

export async function POST(req: Request) {
  const { messages } = await req.json()
  const lastMessage = messages[messages.length - 1]?.content || ''
  const agentType = classifyIntent(lastMessage)

  const apiMessages = [
    { role: 'system', content: AGENT_PROMPTS[agentType] },
    ...messages,
  ]

  const response = await fetch('https://api.z.ai/api/paas/v4/chat/completions', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${process.env.ZAI_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'glm-4.5-flash',
      messages: apiMessages,
      max_tokens: 1000,
      temperature: 0.7,
      stream: true,
    }),
  })

  if (!response.ok) {
    console.error('Z.AI error:', await response.text())
    return new Response(JSON.stringify({ error: 'Failed to get response' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    })
  }

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
          const delta = parsed.choices?.[0]?.delta
          if (delta?.reasoning_content) {
            controller.enqueue(encoder.encode(`0:${JSON.stringify(`⟨thinking⟩${delta.reasoning_content}⟨/thinking⟩`)}\n`))
          }
          if (delta?.content) {
            controller.enqueue(encoder.encode(`0:${JSON.stringify(delta.content)}\n`))
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
