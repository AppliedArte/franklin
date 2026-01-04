# Franklin Adapters

Adapters integrate Franklin with external services.

## Communication Adapters

| Adapter | Provider | File |
|---------|----------|------|
| WhatsApp | WasenderAPI, Twilio, 360dialog | `src/adapters/whatsapp.py` |
| Telegram | Telegram Bot API | `src/adapters/telegram.py` |
| Email | Resend | `src/adapters/email.py` |
| Voice | Vapi.ai | `src/adapters/voice.py` |

## Payment Adapters

Located in `src/adapters/payments/`:

### Privacy.com Adapter

**File:** `privacy.py`

Virtual debit cards with built-in spending limits.

```python
from src.adapters.payments import PrivacyAdapter

adapter = PrivacyAdapter()

# Create virtual card
card = await adapter.create_virtual_card(
    nickname="Travel Expenses",
    spending_limit=Decimal("2000"),
    spending_limit_type="monthly"
)

# List cards
cards = await adapter.list_cards()

# Get transactions
transactions = await adapter.get_transactions(
    card_id=card.card_id,
    limit=50
)
```

**Setup:**
1. Register at [privacy.com](https://privacy.com)
2. Get API key from developer settings
3. Add to `.env`:
   ```
   PRIVACY_API_KEY=your_key
   ```

**Card Types:**
| Type | Behavior |
|------|----------|
| SINGLE_USE | Closes after first transaction |
| MERCHANT_LOCKED | Locks to first merchant used |
| UNLOCKED | Can be used anywhere (premium) |

### Manual Card Adapter

**File:** `manual.py`

For storing any card with encrypted details.

```python
from src.adapters.payments import ManualCardAdapter

adapter = ManualCardAdapter()

# Encrypt card details
encrypted_number = adapter.encrypt("4111111111111111")

# Decrypt for use
card = adapter.get_card_details(
    card_number_encrypted=encrypted_number,
    expiry_encrypted=encrypted_expiry,
    cvv_encrypted=encrypted_cvv
)

# Format for booking APIs
duffel_payload = adapter.format_card_for_duffel(card)
amadeus_payload = adapter.format_card_for_amadeus(card)
stripe_payload = adapter.format_card_for_stripe(card)
```

## Base Interfaces

### PaymentProvider

```python
class PaymentProvider(ABC):
    name: str

    async def create_virtual_card(
        self,
        nickname: str,
        spending_limit: Optional[Decimal],
        spending_limit_type: str,
        merchant: Optional[str]
    ) -> VirtualCard

    async def list_cards(self) -> list[VirtualCard]

    async def get_card(self, card_id: str) -> Optional[VirtualCard]

    async def update_card(
        self,
        card_id: str,
        nickname: Optional[str],
        spending_limit: Optional[Decimal],
        is_active: Optional[bool]
    ) -> VirtualCard

    async def close_card(self, card_id: str) -> bool

    async def get_transactions(
        self,
        card_id: Optional[str],
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        limit: int
    ) -> list[TransactionResult]
```

### Data Classes

```python
@dataclass
class VirtualCard:
    card_id: str
    card_number: str
    expiry_month: str
    expiry_year: str
    cvv: str
    nickname: Optional[str]
    spending_limit: Optional[Decimal]
    is_active: bool
    amount_spent: Decimal

@dataclass
class CardDetails:
    card_number: str
    expiry_month: str
    expiry_year: str
    cvv: str
    billing_name: Optional[str]
    billing_address: Optional[dict]

@dataclass
class TransactionResult:
    success: bool
    transaction_id: Optional[str]
    status: TransactionStatus
    amount: Optional[Decimal]
    merchant: Optional[str]
    timestamp: datetime
```

## Adding New Adapters

1. Create file in `src/adapters/payments/`
2. Extend `PaymentProvider` base class
3. Implement required methods
4. Add to `__init__.py`

```python
# src/adapters/payments/new_provider.py
from src.adapters.payments.base import PaymentProvider, VirtualCard

class NewProviderAdapter(PaymentProvider):
    name = "new_provider"

    async def create_virtual_card(self, ...) -> VirtualCard:
        # Implementation
        pass

    # ... other methods
```
