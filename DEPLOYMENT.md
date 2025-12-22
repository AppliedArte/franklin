# Franklin AI Wealth Advisor - Deployment Guide

## Architecture

- **Website** (Next.js): Vercel at askfranklin.io
- **Backend** (FastAPI): DigitalOcean Droplet at 157.245.224.32

## Droplet Deployment

### SSH Access
```bash
ssh root@157.245.224.32
```

### Pull Latest Code
```bash
cd /opt/aiwealth
git pull origin main
```

### Restart Backend
```bash
# Find and kill existing process
ps aux | grep uvicorn | grep -v grep
kill <PID>

# Start new process
cd /opt/aiwealth
source venv/bin/activate
nohup uvicorn src.main:app --host 0.0.0.0 --port 8000 > /var/log/aiwealth.log 2>&1 &
```

### View Logs
```bash
tail -f /var/log/aiwealth.log
```

### One-liner Deploy
```bash
ssh root@157.245.224.32 "cd /opt/aiwealth && git pull origin main && pkill -f uvicorn; source venv/bin/activate && nohup uvicorn src.main:app --host 0.0.0.0 --port 8000 > /var/log/aiwealth.log 2>&1 &"
```

## Vercel Deployment

Website auto-deploys on git push to main. If not working:
1. Go to https://vercel.com/dashboard
2. Find askfranklin project
3. Click "Redeploy"

## Environment Variables

### Website (.env.local / Vercel)
```
SUPABASE_URL=https://zulxhqoxrhcqsgugkejf.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<key>
VAPI_API_KEY=<key>
VAPI_PHONE_NUMBER_ID=1645417b-76bc-4caf-82e7-366baffc33ff
WASENDER_DEVICE_ID=ace3048eabbf9ad14f72e142f017b24206b5a6cf6fc14026381c98a04e086a19
TELEGRAM_BOT_TOKEN=<token>  # Get from @BotFather
```

## Webhooks

| Service | Webhook URL | Purpose |
|---------|-------------|---------|
| Vapi | https://askfranklin.io/api/vapi/webhook | Call transcripts |
| Wasender | https://askfranklin.io/api/wasender/webhook | WhatsApp messages |
| Telegram | https://askfranklin.io/api/telegram/webhook | Telegram messages |

### Setting Telegram Webhook
After getting bot token from @BotFather:
```bash
curl "https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://askfranklin.io/api/telegram/webhook"
```

## Database Tables (Supabase)

### Required Tables
- `leads` - Form submissions
- `users` - User profiles
- `calls` - Vapi call records
- `user_facts` - Extracted facts from calls
- `whatsapp_messages` - WhatsApp message history
- `telegram_messages` - Telegram message history

## Phone Numbers

- **Vapi (Voice)**: +1 984 477 9472 (US only, need Twilio for international)
- **WhatsApp**: +1 511 201 5524

## Troubleshooting

### Vapi calls failing
- Check VAPI_API_KEY is the private key (not public)
- Verify phone number is assigned to Franklin assistant

### WhatsApp not sending
- Account may be restricted (wait 6 hours)
- Check WASENDER_DEVICE_ID is correct

### Backend not responding
```bash
ssh root@157.245.224.32 "tail -50 /var/log/aiwealth.log"
```
