"""Payment provider adapters for autonomous spending."""

from src.adapters.payments.base import PaymentProvider, CardDetails, TransactionResult
from src.adapters.payments.privacy import PrivacyAdapter
from src.adapters.payments.manual import ManualCardAdapter

__all__ = [
    "PaymentProvider",
    "CardDetails",
    "TransactionResult",
    "PrivacyAdapter",
    "ManualCardAdapter",
]
