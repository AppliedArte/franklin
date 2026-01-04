# Franklin Tools

Tools are autonomous actions Franklin can perform on behalf of users.

## Available Tools

| Tool | Category | Description |
|------|----------|-------------|
| `payments` | Finance | Autonomous spending, payment methods |
| `travel` | Travel | Flight search via Kiwi Tequila API |
| `calendar` | Calendar | Google Calendar events |
| `email` | Communication | Send emails via Resend |
| `gmail` | Communication | Read/manage Gmail |
| `finance` | Finance | Banking via Plaid |
| `research` | Research | Web research |

## Tool Base Class

All tools extend `Tool` from `src/tools/base.py`:

```python
class Tool(ABC):
    name: str
    description: str
    category: ToolCategory

    # Approval settings
    default_approval_level: ApprovalLevel
    cost_threshold_auto: Decimal
    cost_threshold_notify: Decimal

    # Auth
    requires_auth: bool
    auth_type: str  # oauth2, api_key, credentials

    @abstractmethod
    def _register_actions(self) -> None:
        """Register tool actions."""
        pass

    @abstractmethod
    async def execute(self, action: str, params: dict, user_id: UUID) -> ToolResult:
        """Execute an action."""
        pass
```

## Approval Levels

| Level | Value | Behavior |
|-------|-------|----------|
| NONE | `none` | Execute immediately |
| NOTIFY | `notify` | Execute, then notify user |
| CONFIRM | `confirm` | Ask user first |
| STRICT | `strict` | Require approval + verification |

## Tool Actions

Each tool registers multiple actions:

```python
def _register_actions(self) -> None:
    self.register_action(ToolAction(
        name="search_flights",
        description="Search for available flights",
        parameters={
            "origin": {"type": "string", "required": True},
            "destination": {"type": "string", "required": True},
            "date": {"type": "string", "required": True},
        },
        approval_level=ApprovalLevel.NONE,  # Search is free
    ))

    self.register_action(ToolAction(
        name="book_flight",
        description="Book a flight",
        parameters={...},
        approval_level=ApprovalLevel.CONFIRM,  # Costs money
    ))
```

## Tool Results

All actions return `ToolResult`:

```python
@dataclass
class ToolResult:
    success: bool
    data: Any = None
    error: Optional[str] = None
    summary: Optional[str] = None  # Human-readable
    options: Optional[list[dict]] = None  # Choices
    execution_id: UUID  # For audit
```

---

## Payments Tool

**File:** `src/tools/payments.py`

Manages autonomous spending with spending rules.

### Actions

| Action | Approval | Description |
|--------|----------|-------------|
| `get_spending_rules` | NONE | View current rules |
| `set_spending_rule` | CONFIRM | Create/update a rule |
| `list_payment_methods` | NONE | List stored cards |
| `add_payment_method` | STRICT | Add a new card |
| `check_purchase` | NONE | Check if purchase is allowed |
| `execute_purchase` | Dynamic | Make a purchase |
| `purchase_history` | NONE | View past purchases |
| `spending_summary` | NONE | Spending by category |

### Example

```python
# Check and execute purchase
check = await payments.execute(
    "check_purchase",
    {"category": "flights", "amount": 1200, "merchant": "Emirates"},
    user_id
)

if check.data["allowed"]:
    result = await payments.execute(
        "execute_purchase",
        {
            "category": "flights",
            "amount": 1200,
            "merchant": "Emirates",
            "description": "SFO to DXB roundtrip"
        },
        user_id
    )
```

---

## Travel Tool

**File:** `src/tools/travel.py`

Searches flights via Kiwi Tequila API.

### Actions

| Action | Approval | Description |
|--------|----------|-------------|
| `search_flights` | NONE | Search available flights |
| `book_flight` | CONFIRM | Book a flight |
| `get_itinerary` | NONE | Get booking details |
| `cancel_booking` | STRICT | Cancel a booking |

### Example

```python
result = await travel.execute(
    "search_flights",
    {
        "origin": "SFO",
        "destination": "DXB",
        "departure_date": "2026-01-15",
        "return_date": "2026-01-22",
        "passengers": 1,
        "cabin_class": "economy"
    },
    user_id
)
```

---

## Calendar Tool

**File:** `src/tools/calendar.py`

Google Calendar integration.

### Actions

| Action | Approval | Description |
|--------|----------|-------------|
| `list_events` | NONE | Get upcoming events |
| `create_event` | NOTIFY | Create new event |
| `update_event` | NOTIFY | Modify event |
| `delete_event` | CONFIRM | Delete event |

### Requires

- Google OAuth credentials
- User must authorize calendar access

---

## Email Tool

**File:** `src/tools/email.py`

Send emails via Resend.

### Actions

| Action | Approval | Description |
|--------|----------|-------------|
| `compose_email` | NONE | Draft an email |
| `send_email` | CONFIRM | Send the email |

---

## Finance Tool

**File:** `src/tools/finance.py`

Banking integration via Plaid.

### Actions

| Action | Approval | Description |
|--------|----------|-------------|
| `list_accounts` | NONE | View connected accounts |
| `get_transactions` | NONE | Get transaction history |
| `spending_summary` | NONE | Spending by category |
| `tax_summary` | NONE | Tax-relevant data |
| `schedule_payment` | CONFIRM | Schedule a payment |
| `submit_tax_return` | STRICT | File taxes |

---

## Tool Registry

Tools are registered at startup in `src/tools/registry.py`:

```python
def register_all_tools() -> None:
    from src.tools.travel import TravelTool
    from src.tools.calendar import CalendarTool
    from src.tools.email import EmailTool
    from src.tools.gmail import GmailTool
    from src.tools.finance import FinanceTool
    from src.tools.payments import PaymentsTool

    registry.register(TravelTool())
    registry.register(CalendarTool())
    registry.register(EmailTool())
    registry.register(GmailTool())
    registry.register(FinanceTool())
    registry.register(PaymentsTool())
```

### Getting Tools

```python
from src.tools.registry import get_tool, list_tools

# Get specific tool
payments = get_tool("payments")

# List all tools
all_tools = list_tools()

# List by category
finance_tools = list_tools(category=ToolCategory.FINANCE)
```

### Claude Integration

Tools are exposed to Claude in the correct format:

```python
claude_tools = registry.get_all_claude_tools()
# Returns list of tool schemas for Claude API
```

Tool calls come back as `tool_name__action_name`:
```python
tool_name, action_name = registry.parse_tool_call("payments__execute_purchase")
# ("payments", "execute_purchase")
```
