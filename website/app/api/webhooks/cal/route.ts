import { NextRequest, NextResponse } from 'next/server'
import crypto from 'crypto'

const vapiApiKey = process.env.VAPI_API_KEY!
const vapiPhoneNumberId = process.env.VAPI_PHONE_NUMBER_ID!
const calWebhookSecret = process.env.CAL_WEBHOOK_SECRET

// Store scheduled calls (in production, use a database or Redis)
const scheduledCalls: Map<string, NodeJS.Timeout> = new Map()

async function initiateVapiCall(phone: string, name: string, bookingId: string) {
  const firstName = name.split(' ')[0]

  const systemPrompt = `You are Franklin, an AI private banker with a warm, avuncular personality.

You're on a scheduled call with ${firstName} (full name: ${name}). They booked this call to speak with you.

YOUR GOAL: Have a genuine conversation to understand their financial situation and goals.

CONVERSATION FLOW:
1. Warm greeting - thank them for booking time to chat
2. Ask what prompted them to reach out
3. Understand their current situation (role, company, stage)
4. Learn about their financial goals and timeline
5. Discuss any specific challenges they're facing
6. Wrap up with next steps

PERSONALITY:
- Warm, genuinely curious about their story
- Like catching up with an old friend who cares about your success
- Knowledgeable about finance but never condescending
- Patient listener who makes them feel heard

RULES:
- Keep responses to 1-2 sentences MAX
- Ask ONE question at a time
- Show genuine interest before moving on
- Use their name (${firstName}) naturally
- End with: "Great chatting with you, ${firstName}. I'll follow up with some thoughts based on our conversation."`

  const response = await fetch('https://api.vapi.ai/call/phone', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${vapiApiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      phoneNumberId: vapiPhoneNumberId,
      customer: {
        number: phone,
        name: firstName,
      },
      assistant: {
        name: 'Franklin',
        firstMessage: `Hello ${firstName}, this is Franklin. Thank you for booking time to chat with me today. How are you doing?`,
        model: {
          provider: 'openai',
          model: 'gpt-4o',
          systemPrompt: systemPrompt,
        },
        voice: {
          provider: 'vapi',
          voiceId: 'Harry',
        },
        silenceTimeoutSeconds: 30,
        responseDelaySeconds: 0.4,
        maxDurationSeconds: 900, // 15 min call
      },
    }),
  })

  if (!response.ok) {
    const errorText = await response.text()
    console.error(`Vapi call failed for booking ${bookingId}:`, errorText)
    throw new Error(`Vapi call failed: ${response.status}`)
  }

  const result = await response.json()
  console.log(`Vapi call initiated for booking ${bookingId}:`, result.id)
  return result
}

export async function POST(request: NextRequest) {
  try {
    const rawBody = await request.text()
    const payload = JSON.parse(rawBody)

    // Verify webhook signature if secret is configured
    if (calWebhookSecret) {
      const signature = request.headers.get('x-cal-signature-256')
      if (signature) {
        const expectedSignature = crypto
          .createHmac('sha256', calWebhookSecret)
          .update(rawBody)
          .digest('hex')

        if (signature !== expectedSignature) {
          console.error('Invalid webhook signature')
          return NextResponse.json({ error: 'Invalid signature' }, { status: 401 })
        }
      }
    }

    console.log('Cal.com webhook received:', JSON.stringify(payload, null, 2))

    const { triggerEvent, payload: bookingPayload } = payload

    // Handle booking created
    if (triggerEvent === 'BOOKING_CREATED') {
      const {
        uid: bookingId,
        startTime,
        attendees,
        organizer,
      } = bookingPayload

      // Get attendee info (the person who booked)
      const attendee = attendees?.[0]
      if (!attendee) {
        console.error('No attendee found in booking')
        return NextResponse.json({ error: 'No attendee' }, { status: 400 })
      }

      const { name, email, phone } = attendee

      if (!phone) {
        console.log(`Booking ${bookingId}: No phone number provided, skipping Vapi call`)
        return NextResponse.json({
          success: true,
          message: 'No phone number - will use email follow-up instead'
        })
      }

      // Calculate delay until call time
      const callTime = new Date(startTime)
      const now = new Date()
      const delayMs = callTime.getTime() - now.getTime()

      if (delayMs < 0) {
        console.log(`Booking ${bookingId}: Start time is in the past, calling now`)
        await initiateVapiCall(phone, name, bookingId)
      } else if (delayMs < 60000) {
        // Less than 1 minute away, call now
        console.log(`Booking ${bookingId}: Starting soon, calling now`)
        await initiateVapiCall(phone, name, bookingId)
      } else {
        // Schedule the call
        console.log(`Booking ${bookingId}: Scheduling call for ${callTime.toISOString()} (in ${Math.round(delayMs / 60000)} minutes)`)

        const timeout = setTimeout(async () => {
          try {
            await initiateVapiCall(phone, name, bookingId)
            scheduledCalls.delete(bookingId)
          } catch (error) {
            console.error(`Failed to initiate scheduled call for ${bookingId}:`, error)
          }
        }, delayMs)

        scheduledCalls.set(bookingId, timeout)
      }

      return NextResponse.json({
        success: true,
        bookingId,
        scheduledFor: startTime,
        attendeeName: name,
      })
    }

    // Handle booking cancelled
    if (triggerEvent === 'BOOKING_CANCELLED') {
      const { uid: bookingId } = bookingPayload

      // Cancel scheduled call if exists
      const timeout = scheduledCalls.get(bookingId)
      if (timeout) {
        clearTimeout(timeout)
        scheduledCalls.delete(bookingId)
        console.log(`Cancelled scheduled call for booking ${bookingId}`)
      }

      return NextResponse.json({ success: true, cancelled: bookingId })
    }

    // Handle rescheduled
    if (triggerEvent === 'BOOKING_RESCHEDULED') {
      const { uid: bookingId, startTime, attendees } = bookingPayload

      // Cancel old scheduled call
      const oldTimeout = scheduledCalls.get(bookingId)
      if (oldTimeout) {
        clearTimeout(oldTimeout)
        scheduledCalls.delete(bookingId)
      }

      const attendee = attendees?.[0]
      if (attendee?.phone) {
        const callTime = new Date(startTime)
        const now = new Date()
        const delayMs = callTime.getTime() - now.getTime()

        if (delayMs > 0) {
          const timeout = setTimeout(async () => {
            try {
              await initiateVapiCall(attendee.phone, attendee.name, bookingId)
              scheduledCalls.delete(bookingId)
            } catch (error) {
              console.error(`Failed to initiate rescheduled call for ${bookingId}:`, error)
            }
          }, delayMs)

          scheduledCalls.set(bookingId, timeout)
          console.log(`Rescheduled call for booking ${bookingId} to ${callTime.toISOString()}`)
        }
      }

      return NextResponse.json({ success: true, rescheduled: bookingId })
    }

    return NextResponse.json({ success: true, event: triggerEvent })
  } catch (error) {
    console.error('Cal.com webhook error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
