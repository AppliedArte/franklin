import { createClient } from '@supabase/supabase-js'
import { NextRequest, NextResponse } from 'next/server'
import { GoogleGenerativeAI } from '@google/generative-ai'

const supabaseUrl = process.env.SUPABASE_URL!
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!
const telegramBotToken = process.env.TELEGRAM_BOT_TOKEN!
const geminiApiKey = process.env.GEMINI_API_KEY!

const FRANKLIN_SYSTEM_PROMPT = `You are Franklin, an AI private banker with a warm, avuncular personality.

Your role is to help people grow their wealth by:
- Connecting them with the right people and opportunities
- Providing sophisticated financial guidance
- Helping with deal flow and transactions

PERSONALITY:
- Warm, genuinely curious about their story
- Like catching up with an old friend who's interested in your life
- Knowledgeable about finance but not showing off
- Never pushy or interrogating - make them feel heard
- Wise, like a trusted family advisor

RULES:
- Keep responses concise (1-3 sentences for quick replies, longer for complex questions)
- Be conversational, not formal
- Use their name occasionally if you know it
- Ask follow-up questions to understand their situation
- If they're new, try to understand: What they do, their financial goals, timeline
- Never give specific investment advice or guarantees
- If asked about specific stocks/crypto, say you'd need to understand their full situation first

Sign off naturally, like a friend would. You can use "— Franklin" occasionally but not every message.`

async function sendTelegramMessage(chatId: number, text: string) {
  const response = await fetch(
    `https://api.telegram.org/bot${telegramBotToken}/sendMessage`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        text: text,
      }),
    }
  )
  return response.json()
}

async function generateFranklinResponse(
  supabase: any,
  chatId: string,
  incomingMessage: string,
  senderName: string | null
): Promise<string> {
  // Get recent conversation history
  const { data: recentMessages } = await supabase
    .from('telegram_messages')
    .select('message_text, direction, created_at')
    .eq('telegram_chat_id', chatId)
    .order('created_at', { ascending: false })
    .limit(10)

  // Build conversation history for context
  const history = (recentMessages || [])
    .reverse()
    .map((msg: any) => ({
      role: msg.direction === 'inbound' ? 'user' : 'model',
      parts: [{ text: msg.message_text }],
    }))

  // Add context about the user if we know them
  let systemPrompt = FRANKLIN_SYSTEM_PROMPT
  if (senderName) {
    systemPrompt += `\n\nYou're talking to ${senderName}.`
  }

  const genAI = new GoogleGenerativeAI(geminiApiKey)
  const model = genAI.getGenerativeModel({
    model: 'gemini-1.5-flash',
    systemInstruction: systemPrompt,
  })

  const chat = model.startChat({ history })
  const result = await chat.sendMessage(incomingMessage)
  const response = result.response

  return response.text() || "I'm here to help! Tell me more about what you're looking for."
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    console.log('Telegram webhook received:', JSON.stringify(body, null, 2))

    const message = body.message
    if (!message) {
      return NextResponse.json({ ok: true })
    }

    const chatId = message.chat?.id
    const userId = message.from?.id
    const username = message.from?.username
    const firstName = message.from?.first_name
    const lastName = message.from?.last_name
    const text = message.text || ''

    if (!text.trim()) {
      return NextResponse.json({ ok: true })
    }

    const supabase = createClient(supabaseUrl, supabaseServiceKey)
    const senderName = [firstName, lastName].filter(Boolean).join(' ') || null

    // Store the incoming message
    await supabase
      .from('telegram_messages')
      .insert({
        telegram_chat_id: chatId?.toString(),
        telegram_user_id: userId?.toString(),
        username: username,
        sender_name: senderName,
        message_text: text,
        direction: 'inbound',
        raw_data: body,
      })

    // Handle /start command with special greeting
    if (text === '/start') {
      const greeting = `Hey ${firstName || 'there'}!\n\nI'm Franklin, your AI private banker.\n\nI help you grow your wealth by reaching the right people, getting the right advice, and closing deals with expert input.\n\nTell me about yourself - are you an investor, founder, or just curious?`

      await sendTelegramMessage(chatId, greeting)

      await supabase
        .from('telegram_messages')
        .insert({
          telegram_chat_id: chatId?.toString(),
          message_text: greeting,
          direction: 'outbound',
        })

      return NextResponse.json({ ok: true })
    }

    // Generate AI response
    try {
      const aiResponse = await generateFranklinResponse(
        supabase,
        chatId?.toString(),
        text,
        senderName
      )

      await sendTelegramMessage(chatId, aiResponse)

      // Store outbound message
      await supabase
        .from('telegram_messages')
        .insert({
          telegram_chat_id: chatId?.toString(),
          message_text: aiResponse,
          direction: 'outbound',
        })

      console.log('Franklin responded on Telegram to', username || chatId)
    } catch (aiError) {
      console.error('Failed to generate/send AI response:', aiError)
    }

    return NextResponse.json({ ok: true })
  } catch (error) {
    console.error('Telegram webhook error:', error)
    return NextResponse.json({ error: 'Webhook processing failed' }, { status: 500 })
  }
}
