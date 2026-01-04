"""Base payment provider interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional


class TransactionStatus(str, Enum):
    """Status of a card transaction."""
    PENDING = "pending"
    APPROVED = "approved"
    DECLINED = "declined"
    SETTLED = "settled"
    REFUNDED = "refunded"
    VOIDED = "voided"


@dataclass
class CardDetails:
    """Card details for making a transaction."""
    card_number: str
    expiry_month: str
    expiry_year: str
    cvv: str
    billing_name: Optional[str] = None
    billing_address: Optional[dict] = None

    @property
    def expiry(self) -> str:
        year = self.expiry_year[-2:] if len(self.expiry_year) == 4 else self.expiry_year
        return f"{self.expiry_month}/{year}"

    @property
    def last_four(self) -> str:
        return self.card_number[-4:]


@dataclass
class TransactionResult:
    """Result of a card transaction attempt."""
    success: bool
    transaction_id: Optional[str] = None
    status: TransactionStatus = TransactionStatus.PENDING
    authorization_code: Optional[str] = None
    amount: Optional[Decimal] = None
    currency: str = "USD"
    merchant: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    raw_response: Optional[dict] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class VirtualCard:
    """A virtual card from a provider like Privacy.com."""
    card_id: str
    card_number: str
    expiry_month: str
    expiry_year: str
    cvv: str
    nickname: Optional[str] = None
    spending_limit: Optional[Decimal] = None
    spending_limit_type: Optional[str] = None
    merchant_locked: Optional[str] = None
    is_active: bool = True
    amount_spent: Decimal = Decimal("0")
    created_at: datetime = None


class PaymentProvider(ABC):
    """Abstract base class for payment providers."""

    name: str = "base"

    @abstractmethod
    async def create_virtual_card(
        self,
        nickname: str,
        spending_limit: Optional[Decimal] = None,
        spending_limit_type: str = "total",
        merchant: Optional[str] = None,
    ) -> VirtualCard:
        """Create a new virtual card."""
        pass

    @abstractmethod
    async def list_cards(self) -> list[VirtualCard]:
        """List all virtual cards for the account."""
        pass

    @abstractmethod
    async def get_card(self, card_id: str) -> Optional[VirtualCard]:
        """Get a specific card by ID."""
        pass

    @abstractmethod
    async def update_card(
        self,
        card_id: str,
        nickname: Optional[str] = None,
        spending_limit: Optional[Decimal] = None,
        is_active: Optional[bool] = None,
    ) -> VirtualCard:
        """Update card settings."""
        pass

    @abstractmethod
    async def close_card(self, card_id: str) -> bool:
        """Close/deactivate a virtual card."""
        pass

    @abstractmethod
    async def get_transactions(
        self,
        card_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
    ) -> list[TransactionResult]:
        """Get transaction history."""
        pass

    async def make_payment(
        self,
        card: CardDetails,
        amount: Decimal,
        merchant: str,
        description: str,
        currency: str = "USD",
    ) -> TransactionResult:
        """Make a payment using card details.

        Most purchases use external booking APIs (Duffel for flights, etc.).
        This is for direct card-not-present transactions.
        """
        raise NotImplementedError("Direct payments not supported by this provider.")
