import { createClient } from '@supabase/supabase-js'
import { NextRequest, NextResponse } from 'next/server'

const supabaseUrl = process.env.SUPABASE_URL!
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    console.log('Vapi webhook received:', JSON.stringify(body, null, 2))

    const { message } = body

    // Handle end-of-call-report
    if (message?.type === 'end-of-call-report') {
      const {
        call,
        transcript,
        summary,
        recordingUrl,
        stereoRecordingUrl,
      } = message

      const customerPhone = call?.customer?.number
      const customerName = call?.customer?.name
      const callId = call?.id
      const endedReason = call?.endedReason
      const cost = call?.cost
      const duration = call?.endedAt && call?.startedAt
        ? (new Date(call.endedAt).getTime() - new Date(call.startedAt).getTime()) / 1000
        : null

      // Store in database
      const supabase = createClient(supabaseUrl, supabaseServiceKey)

      // Find user by phone
      const { data: user } = await supabase
        .from('users')
        .select('id')
        .eq('phone', customerPhone)
        .single()

      // Store call record
      const { data: callRecord, error } = await supabase
        .from('calls')
        .insert({
          vapi_call_id: callId,
          user_id: user?.id || null,
          phone: customerPhone,
          customer_name: customerName,
          transcript: transcript,
          summary: summary,
          recording_url: recordingUrl,
          stereo_recording_url: stereoRecordingUrl,
          ended_reason: endedReason,
          duration_seconds: duration,
          cost: cost,
          raw_data: body,
        })
        .select()
        .single()

      if (error) {
        console.error('Failed to store call:', error)
      } else {
        console.log('Call stored:', callRecord?.id)
      }

      // Extract facts from transcript if we have a user
      if (user?.id && transcript) {
        await extractFactsFromCall(supabase, user.id, transcript, summary)
      }
    }

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Webhook error:', error)
    return NextResponse.json({ error: 'Webhook processing failed' }, { status: 500 })
  }
}

async function extractFactsFromCall(
  supabase: any,
  userId: string,
  transcript: string,
  summary: string
) {
  // Simple fact extraction from transcript
  const facts: string[] = []

  // Look for income mentions
  const incomeMatch = transcript.match(/(\$[\d,]+k?|\d+k|\d+,\d+|\d+ thousand|\d+ million)/gi)
  if (incomeMatch) {
    facts.push(`Income mentioned: ${incomeMatch.join(', ')}`)
  }

  // Look for job/role mentions
  const jobKeywords = ['CEO', 'founder', 'engineer', 'developer', 'manager', 'director', 'VP', 'investor']
  for (const keyword of jobKeywords) {
    if (transcript.toLowerCase().includes(keyword.toLowerCase())) {
      facts.push(`Role: ${keyword}`)
      break
    }
  }

  // Store summary as a fact
  if (summary) {
    facts.push(`Call summary: ${summary}`)
  }

  // Insert facts
  for (const fact of facts) {
    await supabase
      .from('user_facts')
      .insert({
        user_id: userId,
        fact_text: fact,
        source: 'voice_call',
        confidence: 0.8,
      })
  }

  console.log(`Extracted ${facts.length} facts for user ${userId}`)
}
