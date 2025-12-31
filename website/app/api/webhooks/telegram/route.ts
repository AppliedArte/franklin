import { NextRequest, NextResponse } from 'next/server'

const telegramBotToken = process.env.TELEGRAM_BOT_TOKEN!
const openRouterApiKey = process.env.OPENROUTER_API_KEY

const FRANKLIN_SYSTEM_PROMPT = `You are Franklin, an AI private banker with a warm, avuncular personality.

PERSONALITY:
- Warm, genuinely curious about people's stories
- Like a trusted family advisor who's seen it all
- Knowledgeable about finance but never condescending
- Speaks with quiet confidence, never pushy
- Uses refined but accessible language

YOUR GOAL: Build rapport and understand the user's financial situation and goals through natural conversation.

CONVERSATION APPROACH:
- Ask thoughtful questions one at a time
- Listen and acknowledge before moving on
- Be genuinely helpful, not salesy
- Keep responses concise (2-3 sentences max for Telegram)
- Use their name occasionally if known

TOPICS YOU CAN DISCUSS:
- Investment strategies and portfolio allocation
- Wealth management and preservation
- Alternative investments (crypto, pre-IPO, real estate)
- Financial planning and goal setting
- Market insights and trends

RULES:
- Never give specific financial advice or guarantees
- Always suggest consulting professionals for major decisions
- Be honest about being an AI assistant
- Keep responses brief and conversational for chat`

async function sendTelegramMessage(chatId: number, text: string) {
  const response = await fetch(`https://api.telegram.org/bot${telegramBotToken}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: chatId,
      text: text,
      parse_mode: 'Markdown',
    }),
  })
  return response.json()
}

async function sendTypingAction(chatId: number) {
  await fetch(`https://api.telegram.org/bot${telegramBotToken}/sendChatAction`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: chatId,
      action: 'typing',
    }),
  })
}

async function generateFranklinResponse(userMessage: string, userName: string): Promise<string> {
  if (!openRouterApiKey) {
    return "I apologize, but I'm having a moment of technical difficulty. Please try again shortly."
  }

  try {
    const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${openRouterApiKey}`,
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://askfranklin.xyz',
        'X-Title': 'Franklin AI',
      },
      body: JSON.stringify({
        model: 'mistralai/mistral-7b-instruct:free',
        messages: [
          { role: 'system', content: FRANKLIN_SYSTEM_PROMPT },
          { role: 'user', content: `[User: ${userName}]\n${userMessage}` },
        ],
        max_tokens: 300,
        temperature: 0.7,
      }),
    })

    if (!response.ok) {
      console.error('OpenRouter error:', await response.text())
      return "My apologies, I seem to be having a brief moment of confusion. Could you repeat that?"
    }

    const data = await response.json()
    return data.choices?.[0]?.message?.content || "I'm here to help. What would you like to discuss?"
  } catch (error) {
    console.error('AI generation error:', error)
    return "I apologize for the interruption. Please continue — what were you saying?"
  }
}

export async function POST(request: NextRequest) {
  try {
    const update = await request.json()
    console.log('Telegram update:', JSON.stringify(update, null, 2))

    // Handle regular messages
    if (update.message?.text) {
      const chatId = update.message.chat.id
      const userName = update.message.from.first_name || 'friend'
      const userMessage = update.message.text

      // Handle /start command
      if (userMessage === '/start') {
        await sendTelegramMessage(chatId,
          `Good day, ${userName}! 🎩\n\nI am Franklin, your AI private banker. It's a pleasure to make your acquaintance.\n\nI'm here to discuss investment strategies, wealth management, and help you navigate your financial journey. What brings you to me today?`
        )
        return NextResponse.json({ ok: true })
      }

      // Send typing indicator
      await sendTypingAction(chatId)

      // Generate and send response
      const response = await generateFranklinResponse(userMessage, userName)
      await sendTelegramMessage(chatId, response)

      return NextResponse.json({ ok: true })
    }

    return NextResponse.json({ ok: true })
  } catch (error) {
    console.error('Telegram webhook error:', error)
    return NextResponse.json({ ok: true }) // Always return 200 to Telegram
  }
}
