# AIWealth - AI Wealth Advisor

A modular AI wealth advisor / private banker that analyzes financial status, provides personalized advice, and connects users with services, products, and advisors.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           COMMUNICATION GATEWAY                              │
├─────────────────┬─────────────────┬─────────────────┬──────────────────────┤
│    WhatsApp     │      Voice      │      Email      │      Web Chat        │
│  (WasenderAPI)  │     (Vapi.ai)   │    (Resend)     │    (WebSocket)       │
│                 │                 │                 │                      │
│  /webhooks/     │  /webhooks/     │  /webhooks/     │  /chat/ws/{user}     │
│  whatsapp       │  vapi           │  email          │                      │
└────────┬────────┴────────┬────────┴────────┬────────┴──────────┬───────────┘
         │                 │                 │                   │
         └─────────────────┴─────────────────┴───────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CONVERSATION ORCHESTRATOR                             │
│                         src/agents/orchestrator.py                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Find/create user from channel identifier                                │
│  2. Find/create conversation (24hr session window)                          │
│  3. Assemble context (Boardy-style: profile + history + notes)              │
│  4. Route to appropriate agent based on profile score                       │
│  5. Store messages and update profile                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
         ┌─────────────────────┐       ┌─────────────────────┐
         │   PROFILE BUILDER   │       │   ADVISORY AGENT    │
         │   (score < 30%)     │       │   (score >= 30%)    │
         ├─────────────────────┤       ├─────────────────────┤
         │ Extracts financial  │       │ Provides wealth     │
         │ info through        │       │ guidance based on   │
         │ natural dialogue    │       │ user's profile      │
         └─────────────────────┘       └─────────────────────┘
                                                │
                                                ▼
                                    ┌─────────────────────┐
                                    │   MATCHING ENGINE   │
                                    │   (when appropriate)│
                                    ├─────────────────────┤
                                    │ Connects users to   │
                                    │ advisors, products, │
                                    │ services            │
                                    └─────────────────────┘
```

---

## Core Concepts

### AI Persona: Benjamin "Ben" Franklin

The AI advisor is embodied as **Benjamin Franklin**, a distinguished 1700s upper class British gentleman. This isn't a gimmick - the persona creates:

- **Trust**: A refined, experienced gentleman feels trustworthy with financial matters
- **Warmth**: Avuncular and caring, not cold or robotic
- **Timeless wisdom**: Financial principles that transcend eras
- **Memorable experience**: Users remember conversations with "Ben"

**Speech patterns:**
- "I dare say..." / "Indeed..." / "Most excellent..." / "Frankly speaking..."
- "If I may be so bold..." / "Permit me to suggest..."
- "Never place all eggs in a single basket"

**Persona file:** `src/persona.py` - Edit to customize character

---

### Boardy-Style Context Assembly

Before every LLM call, we assemble full context:

```python
context = {
    "profile_context": "Income: $150k, Goal: early retirement, Risk: moderate...",
    "recent_messages": [...last 20 messages across channels...],
    "internal_notes": ["User prefers async communication", "Interested in crypto"],
    "conversation_summary": "Discussed retirement planning options..."
}
```

This enables:
- **Personalized responses** - AI knows user's full financial picture
- **Cross-channel continuity** - Start on WhatsApp, continue on voice
- **Consistent personality** - AI remembers past interactions

### Profile-First, Then Specialize

```
New User (score: 0%)
    │
    ▼
Profile Builder asks questions naturally
    │
    ▼
Profile grows (income, goals, risk tolerance...)
    │
    ▼
Score reaches 30%+ → Advisory Agent takes over
    │
    ▼
User shows specialized need → Route to specialist module
    │
    ▼
Need exceeds AI capability → Human advisor handoff
```

### Profile Score Calculation

| Field | Weight |
|-------|--------|
| Annual income | 15% |
| Net worth | 15% |
| Primary goal | 20% |
| Risk tolerance | 15% |
| Goal timeline | 10% |
| Liquid assets | 10% |
| Monthly expenses | 10% |
| Interests | 5% |

---

## Project Structure

```
aiwealth/
├── src/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Environment configuration (Pydantic Settings)
│   ├── workers.py              # Background jobs (ARQ/Redis)
│   │
│   ├── api/                    # HTTP endpoints
│   │   ├── health.py           # Health checks (/health, /health/ready)
│   │   ├── webhooks.py         # Channel webhooks (/webhooks/whatsapp, /webhooks/vapi, /webhooks/email)
│   │   └── chat.py             # Web chat API (/chat/message, /chat/ws/{user_id})
│   │
│   ├── adapters/               # External service integrations
│   │   ├── whatsapp.py         # WasenderAPI/Twilio/360dialog
│   │   ├── voice.py            # Vapi.ai integration
│   │   └── email.py            # Resend integration
│   │
│   ├── agents/                 # AI agents (Claude-powered)
│   │   ├── base.py             # Base agent class (Anthropic client)
│   │   ├── orchestrator.py     # Central conversation hub
│   │   ├── profile_builder.py  # Extracts financial info via conversation
│   │   └── advisory.py         # Core wealth guidance agent
│   │
│   ├── matching/               # User-to-service matching
│   │   └── engine.py           # Boardy-style matching logic
│   │
│   ├── db/                     # Database layer
│   │   ├── database.py         # Async PostgreSQL + SQLAlchemy
│   │   └── models.py           # User, UserProfile, Conversation, Message, etc.
│   │
│   └── utils/
│       └── context.py          # Context assembly for LLM calls
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── .gitignore
```

---

## Data Models

### User
```
User
├── id (UUID)
├── name, email, phone, linkedin_url
├── whatsapp_id (channel identifier)
├── is_active, onboarding_completed
├── profile → UserProfile (1:1)
└── conversations → [Conversation] (1:many)
```

### UserProfile
```
UserProfile
├── Financial Snapshot
│   ├── annual_income
│   ├── net_worth
│   ├── liquid_assets
│   ├── monthly_expenses
│   ├── existing_investments (JSON)
│   └── debts (JSON)
│
├── Goals & Preferences
│   ├── primary_goal
│   ├── goal_timeline
│   ├── risk_tolerance (conservative/moderate/aggressive)
│   └── interests (JSON array)
│
├── profile_score (0-100)
└── internal_notes (JSON array) ← Boardy-style behavior observations
```

### Conversation & Message
```
Conversation
├── id, user_id, channel
├── is_active, summary
└── messages → [Message]

Message
├── id, conversation_id
├── role (user/assistant/system)
├── content, channel
├── metadata (JSON)
└── embedding (vector for semantic search)
```

---

## API Endpoints

### Health
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Basic health check |
| GET | `/health/ready` | Readiness check (DB, Redis, LLM) |

### Webhooks (Channel Ingress)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/webhooks/whatsapp` | Incoming WhatsApp messages |
| GET | `/webhooks/whatsapp` | WhatsApp verification |
| POST | `/webhooks/vapi` | Vapi voice transcripts (Custom LLM mode) |
| POST | `/webhooks/email` | Incoming emails |

### Chat (Web Interface)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/chat/message` | Send message, get response |
| WS | `/chat/ws/{user_id}` | Real-time WebSocket chat |
| GET | `/chat/history/{user_id}` | Get conversation history |

---

## Voice Integration (Vapi)

### Custom LLM Mode Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────┐     ┌─────────────┐
│   User      │────▶│   Vapi      │────▶│   AIWealth      │────▶│   Vapi      │
│   speaks    │     │   (STT)     │     │   Orchestrator  │     │   (TTS)     │
└─────────────┘     └─────────────┘     └─────────────────┘     └─────────────┘
                           │                    │                      │
                           │   POST /webhooks/vapi                     │
                           │   {"transcript": "..."}                   │
                           │                    │                      │
                           │                    ▼                      │
                           │            Generate response              │
                           │            with full context              │
                           │                    │                      │
                           │   {"response": "Based on your profile..."} │
                           │◀───────────────────┘                      │
                           │                                           │
                           └──────────────────────────────────────────▶│
                                                                       │
                                                              Speaks to user
```

### Vapi Webhook Events

| Event | Description | Our Action |
|-------|-------------|------------|
| `transcript` | User finished speaking | Generate AI response |
| `end-of-call-report` | Call ended | Store summary for context |
| `hang` | User hung up | Clean up session |

---

## Technology Stack

| Layer | Technology | Why |
|-------|------------|-----|
| **Backend** | Python + FastAPI | Async, great AI libs |
| **LLM** | Claude API (Anthropic) | Best reasoning for financial advice |
| **Database** | PostgreSQL + pgvector | Relational + vector search |
| **Cache/Queue** | Redis + ARQ | Sessions, background jobs |
| **WhatsApp** | WasenderAPI ($6/mo) | Cheapest for validation |
| **Voice** | Vapi.ai (Custom LLM) | Our backend generates responses |
| **Email** | Resend | Developer-friendly |
| **Hosting** | Railway / Render | Simple deployment |

---

## Environment Variables

```bash
# Application
APP_NAME=AIWealth
APP_ENV=development
DEBUG=true
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/aiwealth

# Redis
REDIS_URL=redis://localhost:6379/0

# AI/LLM
ANTHROPIC_API_KEY=your-anthropic-key

# WhatsApp (WasenderAPI)
WASENDER_API_KEY=your-wasender-key
WASENDER_DEVICE_ID=your-device-id

# Voice (Vapi)
VAPI_API_KEY=your-vapi-key

# Email (Resend)
RESEND_API_KEY=your-resend-key
EMAIL_FROM=advisor@yourdomain.com
```

---

## Quick Start

### Local Development

```bash
# 1. Clone and enter directory
cd aiwealth

# 2. Copy environment file
cp .env.example .env
# Edit .env with your API keys

# 3. Start with Docker
docker-compose up -d

# 4. Run database migrations
docker-compose exec app alembic upgrade head

# 5. API is running at http://localhost:8000
```

### Database Migrations (Alembic)

```bash
# Apply all migrations
alembic upgrade head

# Create new migration after model changes
alembic revision --autogenerate -m "description of changes"

# Rollback one migration
alembic downgrade -1

# See current migration status
alembic current
```

### Test the API

```bash
# Health check
curl http://localhost:8000/health

# Test chat
curl -X POST http://localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-user", "message": "Hi, I want to grow my wealth"}'

# Test Vapi webhook
curl -X POST http://localhost:8000/webhooks/vapi \
  -H "Content-Type: application/json" \
  -d '{"message": {"type": "transcript", "transcript": "Hello"}, "call": {"id": "test", "customer": {"number": "+1234567890"}}}'
```

---

## Implementation Status

### Phase 1: Foundation ✅
- [x] FastAPI project structure
- [x] PostgreSQL + pgvector schema
- [x] Core AI engine (Claude API)
- [x] Profile Builder agent
- [x] Context assembly system
- [x] Conversation Orchestrator
- [x] Alembic migrations

### Phase 2: Communication Channels ✅
- [x] WhatsApp adapter (WasenderAPI + Twilio support)
- [x] Voice adapter (Vapi.ai Custom LLM mode)
- [x] Email adapter (Resend)
- [x] Web Chat (REST + WebSocket)
- [x] Unified webhook routing

### Phase 3: Advisory Agents 🚧
- [x] General Advisory Agent
- [ ] Compliance Guard layer
- [ ] Risk Analyzer
- [ ] Profile enrichment automation

### Phase 4: Specialist Modules
- [ ] Specialist module interface
- [ ] Product/Service catalog
- [ ] Routing logic
- [ ] Human advisor handoff

### Phase 5: Matching Engine
- [x] Matching engine skeleton
- [ ] Partner catalog system
- [ ] Introduction workflow
- [ ] Outcome tracking

---

## Cost Estimates (Validation Phase)

| Service | Monthly Cost | Notes |
|---------|-------------|-------|
| WasenderAPI | $6 | WhatsApp messaging |
| Vapi.ai | ~$0.15/min | Pay per use |
| Claude API | ~$3/1M tokens | Pay per use |
| Railway/Render | $5-10 | Hosting |
| PostgreSQL | Included | Railway/Render managed |
| Redis | Included | Railway/Render managed |
| **Total** | ~$20-50/mo | For validation |

---

## License

Private - All rights reserved
