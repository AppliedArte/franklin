import { createClient } from '@supabase/supabase-js'
import { NextRequest, NextResponse } from 'next/server'

const supabaseUrl = process.env.SUPABASE_URL!
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!
const telegramBotToken = process.env.TELEGRAM_BOT_TOKEN!

async function sendTelegramMessage(chatId: number, text: string) {
  const response = await fetch(
    `https://api.telegram.org/bot${telegramBotToken}/sendMessage`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        text: text,
        parse_mode: 'Markdown',
      }),
    }
  )
  return response.json()
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

    const supabase = createClient(supabaseUrl, supabaseServiceKey)

    // Store the message
    const { error } = await supabase
      .from('telegram_messages')
      .insert({
        telegram_chat_id: chatId?.toString(),
        telegram_user_id: userId?.toString(),
        username: username,
        sender_name: [firstName, lastName].filter(Boolean).join(' ') || null,
        message_text: text,
        direction: 'inbound',
        raw_data: body,
      })

    if (error) {
      console.error('Failed to store Telegram message:', error)
    }

    // Handle /start command
    if (text === '/start') {
      await sendTelegramMessage(
        chatId,
        `Hey ${firstName || 'there'}! 👋\n\nI'm *Franklin*, your AI private banker.\n\nI help you grow your wealth by reaching the right people, getting the right advice, and closing deals with expert input.\n\nTell me about yourself - are you an investor, founder, or just curious?`
      )
      return NextResponse.json({ ok: true })
    }

    // Auto-reply for now (can be enhanced with AI later)
    await sendTelegramMessage(
      chatId,
      `Thanks for your message, ${firstName || 'friend'}! I've noted it down.\n\nI'll get back to you shortly. In the meantime, feel free to share more about what you're working on.`
    )

    return NextResponse.json({ ok: true })
  } catch (error) {
    console.error('Telegram webhook error:', error)
    return NextResponse.json({ error: 'Webhook processing failed' }, { status: 500 })
  }
}
