"""Trigger definitions for proactive behavior."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional
from uuid import UUID, uuid4


class TriggerType(str, Enum):
    """Types of triggers."""
    SCHEDULED = "scheduled"  # Cron-based
    EVENT = "event"  # Event-driven (calendar, price change, etc.)
    CONDITION = "condition"  # Condition-based (balance drops, deadline approaching)
    REMINDER = "reminder"  # User-set reminders


class TriggerAction(str, Enum):
    """Actions a trigger can take."""
    NOTIFY = "notify"  # Send a notification
    SUGGEST = "suggest"  # Suggest an action (with approval)
    EXECUTE = "execute"  # Auto-execute (low-risk only)
    PREPARE = "prepare"  # Prepare something for user review


@dataclass
class Trigger:
    """A trigger event that activates proactive behavior."""
    id: UUID = field(default_factory=uuid4)
    type: TriggerType = TriggerType.SCHEDULED
    name: str = ""
    description: str = ""
    condition: dict = field(default_factory=dict)  # Trigger conditions
    action: TriggerAction = TriggerAction.NOTIFY
    tool: Optional[str] = None  # Tool to use if any
    tool_action: Optional[str] = None
    parameters: dict = field(default_factory=dict)
    message_template: str = ""
    is_active: bool = True
    last_triggered: Optional[datetime] = None
    next_trigger: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "type": self.type.value,
            "name": self.name,
            "description": self.description,
            "action": self.action.value,
            "is_active": self.is_active,
            "last_triggered": self.last_triggered.isoformat() if self.last_triggered else None,
            "next_trigger": self.next_trigger.isoformat() if self.next_trigger else None,
        }


@dataclass
class TriggerRule:
    """A rule for when to trigger proactive behavior."""
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    trigger_type: TriggerType = TriggerType.CONDITION
    description: str = ""

    # For SCHEDULED type
    cron_expression: Optional[str] = None  # "0 9 * * *" = 9am daily
    timezone: str = "UTC"

    # For EVENT type
    event_source: Optional[str] = None  # "calendar", "price", "email"
    event_filter: dict = field(default_factory=dict)

    # For CONDITION type
    check_interval_minutes: int = 60
    condition_expression: str = ""  # Evaluated expression

    # Action to take
    action: TriggerAction = TriggerAction.NOTIFY
    action_config: dict = field(default_factory=dict)

    # Constraints
    max_triggers_per_day: int = 3
    cooldown_hours: int = 4
    user_can_disable: bool = True

    is_active: bool = True
    priority: int = 5  # 1-10, higher = more important


# Default trigger rules
DEFAULT_TRIGGERS = [
    # Travel-related
    TriggerRule(
        name="trip_booking_reminder",
        trigger_type=TriggerType.CONDITION,
        description="Remind to book flights for upcoming calendar trips",
        condition_expression="calendar.event.title contains 'trip' and calendar.event.start - now() < 14 days and not booking.exists",
        action=TriggerAction.SUGGEST,
        action_config={
            "tool": "travel",
            "action": "search_flights",
            "message": "I noticed you have a trip to {destination} coming up in {days} days. Would you like me to search for flights?",
        },
        check_interval_minutes=1440,  # Daily
        max_triggers_per_day=1,
    ),

    # Finance-related
    TriggerRule(
        name="tax_deadline_reminder",
        trigger_type=TriggerType.SCHEDULED,
        description="Remind about tax filing deadlines",
        cron_expression="0 9 1 4 *",  # April 1st, 9am
        action=TriggerAction.NOTIFY,
        action_config={
            "message": "Tax filing deadline is approaching (April 15). Would you like me to help prepare your tax documents?",
        },
        max_triggers_per_day=1,
    ),

    TriggerRule(
        name="low_balance_alert",
        trigger_type=TriggerType.CONDITION,
        description="Alert when checking account balance drops below threshold",
        condition_expression="account.balance < user.settings.low_balance_threshold",
        action=TriggerAction.NOTIFY,
        action_config={
            "message": "Your {account_name} balance is ${balance}, below your ${threshold} threshold.",
        },
        check_interval_minutes=60,
        cooldown_hours=24,
    ),

    TriggerRule(
        name="unusual_spending",
        trigger_type=TriggerType.CONDITION,
        description="Alert on unusual spending patterns",
        condition_expression="spending.today > spending.daily_average * 2",
        action=TriggerAction.NOTIFY,
        action_config={
            "message": "I noticed higher than usual spending today (${amount} vs ${average} average). Everything okay?",
        },
        check_interval_minutes=120,
        cooldown_hours=24,
    ),

    # Calendar-related
    TriggerRule(
        name="meeting_prep",
        trigger_type=TriggerType.CONDITION,
        description="Prepare meeting notes before important meetings",
        condition_expression="calendar.event.start - now() < 1 hour and calendar.event.attendees > 3",
        action=TriggerAction.PREPARE,
        action_config={
            "tool": "email",
            "action": "search",
            "message": "You have a meeting with {attendees} in {time}. Here's relevant context from your recent emails...",
        },
        check_interval_minutes=30,
    ),

    # Email-related
    TriggerRule(
        name="urgent_email_alert",
        trigger_type=TriggerType.EVENT,
        description="Alert on urgent emails from VIPs",
        event_source="email",
        event_filter={"from": "vip_list", "subject_contains": ["urgent", "asap", "important"]},
        action=TriggerAction.NOTIFY,
        action_config={
            "message": "Urgent email from {sender}: {subject}",
        },
    ),

    # Price alerts
    TriggerRule(
        name="flight_price_drop",
        trigger_type=TriggerType.CONDITION,
        description="Alert when saved flight search prices drop",
        condition_expression="saved_search.current_price < saved_search.original_price * 0.85",
        action=TriggerAction.SUGGEST,
        action_config={
            "tool": "travel",
            "action": "search_flights",
            "message": "The flight you were watching ({route}) dropped 15% to ${price}. Book now?",
        },
        check_interval_minutes=360,  # Every 6 hours
    ),

    TriggerRule(
        name="stock_alert",
        trigger_type=TriggerType.CONDITION,
        description="Alert on significant stock price movements",
        condition_expression="watchlist.stock.change_pct > 5 or watchlist.stock.change_pct < -5",
        action=TriggerAction.NOTIFY,
        action_config={
            "message": "{symbol} moved {change}% today (${price}). {direction} {reason}.",
        },
        check_interval_minutes=30,
    ),
]


def get_default_triggers() -> list[TriggerRule]:
    """Get default trigger rules."""
    return DEFAULT_TRIGGERS.copy()
