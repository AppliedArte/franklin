# Autonomous Payments Module

Franklin can spend money on your behalf within pre-defined rules. No constant approval needed.

## Overview

The payments module enables Franklin to execute purchases autonomously based on user-defined spending rules. This creates a "trusted assistant" experience where Franklin handles transactions without requiring approval for every purchase.

```
User: "Book me a flight to Dubai next Friday"
Franklin: *checks rules* → *books flight* → *sends confirmation*
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      PAYMENTS MODULE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Spending   │    │   Payment    │    │   Purchase   │      │
│  │    Rules     │    │   Methods    │    │   History    │      │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘      │
│         │                   │                   │               │
│         └───────────────────┼───────────────────┘               │
│                             │                                    │
│                    ┌────────▼────────┐                          │
│                    │  PaymentsTool   │                          │
│                    │  (Executor)     │                          │
│                    └────────┬────────┘                          │
│                             │                                    │
│         ┌───────────────────┼───────────────────┐               │
│         ▼                   ▼                   ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ Privacy.com  │    │    Lithic    │    │    Manual    │      │
│  │   Adapter    │    │   Adapter    │    │   Adapter    │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Spending Rules (`SpendingRule`)

Define what Franklin can auto-approve vs. what needs confirmation.

```python
SpendingRule:
    category: str          # flights, hotels, subscriptions, etc.
    auto_approve_under: float   # Just do it (no notification)
    notify_only_under: float    # Do it, tell me after
    max_per_transaction: float  # Hard limit per purchase
    max_daily: float           # Daily spending cap
    max_monthly: float         # Monthly spending cap
    preferences: dict          # Category-specific (airline class, hotel stars)
```

**Example Rules:**

| Category | Auto-Approve | Notify Under | Max/Transaction |
|----------|--------------|--------------|-----------------|
| flights | $500 | $2,000 | $3,000 |
| hotels | $200 | $500 | $1,000 |
| subscriptions | $50 | $100 | $200 |
| general | $100 | $500 | $1,000 |

### 2. Payment Methods (`PaymentMethod`)

Stored payment methods for executing purchases.

```python
PaymentMethod:
    provider: str              # privacy, lithic, manual
    nickname: str              # "Travel Card", "Subscriptions"
    card_number_encrypted: str # Fernet-encrypted
    expiry_encrypted: str
    cvv_encrypted: str
    spending_limit: float      # Provider-level failsafe
    is_default: bool
```

**Supported Providers:**

| Provider | Type | Best For |
|----------|------|----------|
| Privacy.com | Virtual cards | Consumer use, built-in limits |
| Lithic | Card issuing API | Programmatic control |
| Manual | Any card | Flexibility, self-managed limits |

### 3. Purchase Tracking (`Purchase`)

Full audit trail of all purchases.

```python
Purchase:
    category: str
    merchant: str
    amount: float
    status: str               # pending, processing, completed, failed
    approval_required: bool
    approved_at: datetime
    approval_method: str      # auto, whatsapp, telegram
    purchase_data: dict       # Flight details, hotel info, etc.
    confirmation_number: str
```

## Approval Flow

```
Purchase Request
       │
       ▼
┌──────────────────┐
│ Check Spending   │
│ Rules            │
└────────┬─────────┘
         │
    ┌────┴────┬────────────┬─────────────┐
    ▼         ▼            ▼             ▼
 No Rule   Under        Under         Above
           Auto-Approve  Notify        Notify
    │         │            │             │
    ▼         ▼            ▼             ▼
  CONFIRM   EXECUTE     EXECUTE       CONFIRM
  (ask)    (silent)    + NOTIFY      (ask user)
```

### Approval Levels

| Level | Behavior | Example |
|-------|----------|---------|
| `NONE` | Execute immediately, no notification | $30 subscription |
| `NOTIFY` | Execute, then notify user | $800 flight |
| `CONFIRM` | Ask user first, wait for approval | $2,500 hotel |
| `STRICT` | Require approval + verification | Exceeds limits |

## API Actions

### Spending Rules

```python
# Get current rules
payments.get_spending_rules(category="flights")

# Set a rule
payments.set_spending_rule(
    category="flights",
    auto_approve_under=500,
    notify_only_under=2000,
    max_per_transaction=3000,
    preferences={"class": "economy", "max_stops": 1}
)
```

### Payment Methods

```python
# List methods
payments.list_payment_methods()

# Add a card
payments.add_payment_method(
    nickname="Travel Card",
    method_type="virtual_card",
    provider="privacy",
    card_number="4111111111111111",
    expiry="12/25",
    cvv="123",
    spending_limit=5000,
    set_as_default=True
)
```

### Purchases

```python
# Check if purchase is allowed
payments.check_purchase(
    category="flights",
    amount=1200,
    merchant="Emirates"
)

# Execute purchase
payments.execute_purchase(
    category="flights",
    amount=1200,
    merchant="Emirates",
    description="SFO to DXB, Jan 15-22",
    purchase_data={
        "flight_number": "EK226",
        "departure": "2026-01-15T10:30:00",
        "arrival": "2026-01-16T08:45:00"
    }
)

# Get history
payments.purchase_history(category="flights", days=30)

# Get summary
payments.spending_summary(period="month")
```

## Security

### Encryption

Card details are encrypted at rest using Fernet symmetric encryption:

```python
from cryptography.fernet import Fernet

# Generate key (do once, store in OAUTH_ENCRYPTION_KEY)
key = Fernet.generate_key()

# Encrypt card number
fernet = Fernet(key)
encrypted = fernet.encrypt(card_number.encode())
```

### Virtual Card Limits

Privacy.com cards have built-in spending limits as a failsafe:

```
User sets rule: max $2000/transaction
Privacy.com card: max $3000/month

Even if a bug bypasses the software limit,
the card itself will decline transactions over $3000
```

### Audit Trail

Every purchase is logged with:
- Timestamp
- User ID
- Amount and merchant
- Approval method (auto/manual)
- Success/failure status
- Error messages if failed

## Setup

### 1. Environment Variables

```bash
# Required for encryption
OAUTH_ENCRYPTION_KEY=your-fernet-key

# Privacy.com (recommended)
PRIVACY_API_KEY=your-api-key

# Default limits
DEFAULT_APPROVAL_THRESHOLD=100.0
DEFAULT_MAX_PER_TRANSACTION=500.0
DEFAULT_DAILY_LIMIT=2000.0
DEFAULT_MONTHLY_LIMIT=10000.0
```

### 2. Database Migration

```bash
alembic upgrade head
```

This creates:
- `spending_rules` table
- `payment_methods` table
- `purchases` table

### 3. Add Payment Method

Via conversation:
```
"Add my Privacy card ending in 4242 as my default payment method"
```

Or via API:
```python
await payments_tool.execute(
    "add_payment_method",
    {...},
    user_id
)
```

### 4. Set Spending Rules

Via conversation:
```
"For flights, auto-approve under $500, notify me under $2000"
```

## File Structure

```
src/
├── tools/
│   └── payments.py          # PaymentsTool - main tool class
│
├── adapters/
│   └── payments/
│       ├── __init__.py
│       ├── base.py          # PaymentProvider interface
│       ├── privacy.py       # Privacy.com adapter
│       └── manual.py        # Manual card storage
│
└── db/
    └── models.py            # SpendingRule, PaymentMethod, Purchase

alembic/versions/
└── 006_add_payments_module.py
```

## Integration with Other Tools

The payments module integrates with:

| Tool | Integration |
|------|-------------|
| **TravelTool** | Books flights using stored payment method |
| **CalendarTool** | Adds booked trips to calendar |
| **EmailTool** | Sends booking confirmations |
| **WhatsApp/Telegram** | Receives approval requests, sends confirmations |

## Example Conversation

```
User: "I need to be in Dubai for a meeting next Friday"

Franklin: I found 3 flights to Dubai:
1. Emirates EK226 - $1,180 (Direct, 16h)
2. Qatar QR100 - $980 (1 stop, 18h)
3. Etihad EY123 - $1,050 (Direct, 16h)

Based on your preferences (direct flights, Emirates),
I'll book option 1. This is under your $2,000 notify
threshold, so I'll proceed and send confirmation.

*books flight*

Done! Confirmation #EK7X92K. Emirates EK226, Jan 10,
departing SFO 10:30 PM, arriving DXB 8:45 PM+1.
Added to your calendar.
```
