import { createClient } from '@supabase/supabase-js'
import { NextRequest, NextResponse } from 'next/server'

const supabaseUrl = process.env.SUPABASE_URL!
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!
const webhookSecret = process.env.WASENDER_WEBHOOK_SECRET

export async function POST(request: NextRequest) {
  try {
    // Optionally verify webhook signature
    if (webhookSecret) {
      const signature = request.headers.get('X-Webhook-Signature')
      if (signature !== webhookSecret) {
        console.error('Invalid webhook signature')
        return NextResponse.json({ error: 'Invalid signature' }, { status: 401 })
      }
    }

    const body = await request.json()
    console.log('Wasender webhook received:', JSON.stringify(body, null, 2))

    const { event, timestamp, data } = body

    // Handle incoming messages
    if (event === 'messages.received') {
      const message = data?.messages
      if (!message) {
        return NextResponse.json({ success: true })
      }

      const senderPhone = message.key?.cleanedSenderPn ||
                          message.key?.remoteJid?.replace('@s.whatsapp.net', '') ||
                          message.key?.senderPn?.replace('@s.whatsapp.net', '')
      const messageId = message.key?.id
      const messageBody = message.messageBody || message.message?.conversation || ''
      const fromMe = message.key?.fromMe || false

      // Don't store our own outgoing messages
      if (fromMe) {
        return NextResponse.json({ success: true })
      }

      const supabase = createClient(supabaseUrl, supabaseServiceKey)

      // Find user by phone
      const { data: user } = await supabase
        .from('users')
        .select('id, name')
        .eq('phone', senderPhone)
        .single()

      // Also check leads table
      const { data: lead } = await supabase
        .from('leads')
        .select('id, name, phone')
        .eq('phone', senderPhone)
        .single()

      // Store the message
      const { data: storedMessage, error } = await supabase
        .from('whatsapp_messages')
        .insert({
          wasender_message_id: messageId,
          phone: senderPhone,
          user_id: user?.id || null,
          lead_id: lead?.id || null,
          sender_name: user?.name || lead?.name || null,
          message_body: messageBody,
          direction: 'inbound',
          raw_data: body,
          received_at: timestamp ? new Date(timestamp * 1000).toISOString() : new Date().toISOString(),
        })
        .select()
        .single()

      if (error) {
        console.error('Failed to store WhatsApp message:', error)
      } else {
        console.log('WhatsApp message stored:', storedMessage?.id)
      }
    }

    // Always respond 200 quickly
    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Wasender webhook error:', error)
    return NextResponse.json({ error: 'Webhook processing failed' }, { status: 500 })
  }
}
