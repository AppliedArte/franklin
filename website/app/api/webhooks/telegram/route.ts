import { NextRequest, NextResponse } from 'next/server'
import { getConversationHistory, saveMessage, getUserProfile, addUserFact, buildContextPrompt, Message } from '@/lib/memory'
import { classifyIntent, AGENT_PROMPTS, extractFacts, AgentType } from '@/lib/agents'

const telegramBotToken = process.env.TELEGRAM_BOT_TOKEN!
const zaiApiKey = process.env.ZAI_API_KEY

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

async function generateFranklinResponse(
  userMessage: string,
  userName: string,
  agentType: AgentType,
  conversationHistory: Message[],
  contextPrompt: string
): Promise<string> {
  if (!zaiApiKey) {
    return "I apologize, but I'm having a moment of technical difficulty. Please try again shortly."
  }

  try {
    // Build messages array with history
    const messages: Array<{ role: string; content: string }> = []

    // System prompt based on agent type
    let systemPrompt = AGENT_PROMPTS[agentType]

    // Add user context if available
    if (contextPrompt) {
      systemPrompt += contextPrompt
    }

    messages.push({ role: 'system', content: systemPrompt })

    // Add conversation history (last 6 messages for context)
    for (const msg of conversationHistory.slice(-6)) {
      messages.push({ role: msg.role, content: msg.content })
    }

    // Add current message
    messages.push({ role: 'user', content: `[${userName}]: ${userMessage}` })

    // Call Z.AI
    const response = await fetch('https://api.z.ai/api/coding/paas/v4/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${zaiApiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'GLM-4.7',
        messages,
        max_tokens: 1000,
        temperature: 0.7,
      }),
    })

    if (!response.ok) {
      console.error('Z.AI error:', await response.text())
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
      const odStr = chatId.toString()
      const userName = update.message.from.first_name || 'friend'
      const userMessage = update.message.text

      // Send typing indicator immediately
      await sendTypingAction(chatId)

      // Get user profile and conversation history in parallel
      const [userProfile, conversationHistory] = await Promise.all([
        getUserProfile(odStr, 'telegram', userName),
        getConversationHistory(odStr, 'telegram', 10),
      ])

      // Build context from user profile
      const contextPrompt = buildContextPrompt(userProfile, conversationHistory)

      // Classify intent and route to appropriate agent
      const agentType = classifyIntent(userMessage)
      console.log(`[${userName}] Intent: ${agentType} | Message: ${userMessage.substring(0, 50)}...`)

      // Generate response with context
      const response = await generateFranklinResponse(
        userMessage,
        userName,
        agentType,
        conversationHistory,
        contextPrompt
      )

      // Save both messages to conversation history (fire and forget)
      saveMessage(odStr, 'telegram', 'user', userMessage).catch(console.error)
      saveMessage(odStr, 'telegram', 'assistant', response).catch(console.error)

      // Extract and save any facts from the conversation
      const facts = extractFacts(userMessage, response)
      for (const fact of facts) {
        addUserFact(odStr, 'telegram', fact).catch(console.error)
      }

      // Send response
      await sendTelegramMessage(chatId, response)

      return NextResponse.json({ ok: true })
    }

    return NextResponse.json({ ok: true })
  } catch (error) {
    console.error('Telegram webhook error:', error)
    return NextResponse.json({ ok: true }) // Always return 200 to Telegram
  }
}
