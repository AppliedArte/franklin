"""Manual card adapter for directly stored card details.

Handles cards manually entered and stored encrypted in the database.
Card details are encrypted at rest using Fernet encryption.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from cryptography.fernet import Fernet

from src.config import get_settings
from src.adapters.payments.base import (
    PaymentProvider, VirtualCard, CardDetails, TransactionResult, TransactionStatus
)

settings = get_settings()


class ManualCardAdapter(PaymentProvider):
    """Adapter for manually stored card details."""

    name = "manual"

    def __init__(self):
        encryption_key = getattr(settings, 'oauth_encryption_key', '')
        self.fernet = Fernet(encryption_key.encode()) if encryption_key else None

    def encrypt(self, value: str) -> str:
        if not self.fernet:
            raise ValueError("Encryption key not configured")
        return self.fernet.encrypt(value.encode()).decode()

    def decrypt(self, encrypted_value: str) -> str:
        if not self.fernet:
            raise ValueError("Encryption key not configured")
        return self.fernet.decrypt(encrypted_value.encode()).decode()

    def get_card_details(
        self,
        card_number_encrypted: str,
        expiry_encrypted: str,
        cvv_encrypted: str,
        billing_name: Optional[str] = None,
        billing_address: Optional[dict] = None,
    ) -> CardDetails:
        """Decrypt and return card details for use in a transaction."""
        expiry_month, expiry_year = self.decrypt(expiry_encrypted).split("/")
        return CardDetails(
            card_number=self.decrypt(card_number_encrypted),
            expiry_month=expiry_month,
            expiry_year=expiry_year,
            cvv=self.decrypt(cvv_encrypted),
            billing_name=billing_name,
            billing_address=billing_address,
        )

    def format_card_for_duffel(self, card: CardDetails) -> dict:
        """Format card details for Duffel API (flights)."""
        year = f"20{card.expiry_year}" if len(card.expiry_year) == 2 else card.expiry_year
        addr = card.billing_address or {}
        return {
            "type": "credit_card",
            "card_number": card.card_number,
            "expiry_month": card.expiry_month,
            "expiry_year": year,
            "cvc": card.cvv,
            "name": card.billing_name or "Cardholder",
            "address_line_1": addr.get("line1", ""),
            "address_city": addr.get("city", ""),
            "address_postal_code": addr.get("postal_code", ""),
            "address_country_code": addr.get("country", "US"),
        }

    def format_card_for_amadeus(self, card: CardDetails) -> dict:
        """Format card details for Amadeus API (flights)."""
        return {
            "vendorCode": self._detect_card_brand(card.card_number),
            "cardNumber": card.card_number,
            "expiryDate": f"{card.expiry_year}-{card.expiry_month}",
            "holderName": card.billing_name or "CARDHOLDER",
        }

    def format_card_for_stripe(self, card: CardDetails) -> dict:
        """Format for Stripe-style APIs."""
        year = f"20{card.expiry_year}" if len(card.expiry_year) == 2 else card.expiry_year
        return {
            "number": card.card_number,
            "exp_month": int(card.expiry_month),
            "exp_year": int(year),
            "cvc": card.cvv,
            "name": card.billing_name,
        }

    @staticmethod
    def _detect_card_brand(card_number: str) -> str:
        """Detect card brand from number."""
        if not card_number:
            return "VI"
        first_digit = card_number[0]
        first_two = card_number[:2]

        if first_digit == "4":
            return "VI"
        elif first_two in ["51", "52", "53", "54", "55"]:
            return "CA"
        elif first_two in ["34", "37"]:
            return "AX"
        elif first_two in ["60", "65"]:
            return "DC"
        return "VI"

    # Virtual card operations not supported for manual cards
    async def create_virtual_card(self, nickname: str, spending_limit: Optional[Decimal] = None,
                                   spending_limit_type: str = "total", merchant: Optional[str] = None) -> VirtualCard:
        raise NotImplementedError("Cannot create virtual cards with manual adapter.")

    async def list_cards(self) -> list[VirtualCard]:
        return []

    async def get_card(self, card_id: str) -> Optional[VirtualCard]:
        return None

    async def update_card(self, card_id: str, nickname: Optional[str] = None,
                         spending_limit: Optional[Decimal] = None, is_active: Optional[bool] = None) -> VirtualCard:
        raise NotImplementedError("Use database operations to update manual cards")

    async def close_card(self, card_id: str) -> bool:
        raise NotImplementedError("Use database operations to deactivate manual cards")

    async def get_transactions(self, card_id: Optional[str] = None, start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None, limit: int = 50) -> list[TransactionResult]:
        return []
