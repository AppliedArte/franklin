"""Privacy.com virtual card adapter.

Privacy.com provides virtual debit cards with spending limits - perfect for
giving an AI agent controlled spending ability.

Features:
- Create virtual cards with per-merchant or total spending limits
- Instant card creation
- Transaction notifications
- Pause/close cards anytime

API Docs: https://privacy.com/developer/docs
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

import httpx

from src.config import get_settings
from src.adapters.payments.base import (
    PaymentProvider, VirtualCard, TransactionResult, TransactionStatus
)

settings = get_settings()


class PrivacyAdapter(PaymentProvider):
    """Privacy.com virtual card adapter."""

    name = "privacy"
    BASE_URL = "https://api.privacy.com/v1"

    def __init__(self):
        self.api_key = getattr(settings, 'privacy_api_key', '')

    async def _request(self, method: str, endpoint: str, data: Optional[dict] = None) -> dict:
        """Make API request to Privacy.com."""
        if not self.api_key:
            raise ValueError("Privacy.com API key not configured")

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"{self.BASE_URL}{endpoint}",
                headers={"Authorization": f"api-key {self.api_key}", "Content-Type": "application/json"},
                json=data,
                timeout=30.0,
            )

            if response.status_code >= 400:
                error_data = response.json() if response.content else {}
                raise Exception(
                    f"Privacy.com API error {response.status_code}: "
                    f"{error_data.get('message', response.text)}"
                )

            return response.json() if response.content else {}

    def _parse_card(self, data: dict) -> VirtualCard:
        """Parse API response into VirtualCard."""
        return VirtualCard(
            card_id=data["token"],
            card_number=data.get("pan", ""),  # Only returned on creation
            expiry_month=data.get("exp_month", ""),
            expiry_year=data.get("exp_year", ""),
            cvv=data.get("cvv", ""),
            nickname=data.get("memo", ""),
            spending_limit=Decimal(str(data.get("spend_limit", 0))) / 100 if data.get("spend_limit") else None,
            spending_limit_type=data.get("spend_limit_duration", "").lower() or "total",
            merchant_locked=data.get("funding", {}).get("account_name"),
            is_active=data.get("state") == "OPEN",
            amount_spent=Decimal(str(data.get("spend", 0))) / 100,
            created_at=datetime.fromisoformat(data["created"].replace("Z", "+00:00")) if data.get("created") else None,
        )

    def _parse_transaction(self, data: dict) -> TransactionResult:
        """Parse transaction data."""
        status_map = {
            "PENDING": TransactionStatus.PENDING,
            "APPROVED": TransactionStatus.APPROVED,
            "DECLINED": TransactionStatus.DECLINED,
            "SETTLED": TransactionStatus.SETTLED,
            "VOIDED": TransactionStatus.VOIDED,
        }

        return TransactionResult(
            success=data.get("status") in ["APPROVED", "SETTLED"],
            transaction_id=data.get("token"),
            status=status_map.get(data.get("status"), TransactionStatus.PENDING),
            amount=Decimal(str(data.get("amount", 0))) / 100,
            currency="USD",  # Privacy.com is USD only
            merchant=data.get("merchant", {}).get("descriptor", ""),
            timestamp=datetime.fromisoformat(data["created"].replace("Z", "+00:00")) if data.get("created") else None,
            raw_response=data,
        )

    async def create_virtual_card(
        self,
        nickname: str,
        spending_limit: Optional[Decimal] = None,
        spending_limit_type: str = "total",
        merchant: Optional[str] = None,
    ) -> VirtualCard:
        """Create a new Privacy.com virtual card."""
        type_map = {
            "per_transaction": "TRANSACTION",
            "monthly": "MONTHLY",
            "yearly": "ANNUALLY",
            "total": "FOREVER",
        }

        data = {"memo": nickname, "type": "MERCHANT_LOCKED"}

        if spending_limit:
            data["spend_limit"] = int(spending_limit * 100)
            data["spend_limit_duration"] = type_map.get(spending_limit_type, "FOREVER")

        response = await self._request("POST", "/card", data)
        return self._parse_card(response)

    async def list_cards(self) -> list[VirtualCard]:
        """List all cards."""
        response = await self._request("GET", "/card")
        return [self._parse_card(c) for c in response.get("data", [])]

    async def get_card(self, card_id: str) -> Optional[VirtualCard]:
        """Get card by token."""
        try:
            response = await self._request("GET", f"/card?card_token={card_id}")
            cards = response.get("data", [])
            return self._parse_card(cards[0]) if cards else None
        except Exception:
            return None

    async def update_card(
        self,
        card_id: str,
        nickname: Optional[str] = None,
        spending_limit: Optional[Decimal] = None,
        is_active: Optional[bool] = None,
    ) -> VirtualCard:
        """Update card settings."""
        data = {"card_token": card_id}

        if nickname is not None:
            data["memo"] = nickname
        if spending_limit is not None:
            data["spend_limit"] = int(spending_limit * 100)
        if is_active is not None:
            data["state"] = "OPEN" if is_active else "PAUSED"

        response = await self._request("PUT", "/card", data)
        return self._parse_card(response)

    async def close_card(self, card_id: str) -> bool:
        """Close a card permanently."""
        try:
            await self._request("PUT", "/card", {
                "card_token": card_id,
                "state": "CLOSED",
            })
            return True
        except Exception:
            return False

    async def get_transactions(
        self,
        card_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
    ) -> list[TransactionResult]:
        """Get transaction history."""
        params = [f"page_size={limit}"]
        if card_id:
            params.append(f"card_token={card_id}")
        if start_date:
            params.append(f"begin={start_date.strftime('%Y-%m-%d')}")
        if end_date:
            params.append(f"end={end_date.strftime('%Y-%m-%d')}")

        endpoint = f"/transaction?{'&'.join(params)}"
        response = await self._request("GET", endpoint)
        return [self._parse_transaction(t) for t in response.get("data", [])]

    async def simulate_authorization(
        self,
        card_id: str,
        amount: Decimal,
        merchant: str = "Test Merchant",
    ) -> TransactionResult:
        """Simulate a transaction (sandbox only)."""
        data = {
            "descriptor": merchant,
            "pan": card_id,
            "amount": int(amount * 100),
        }
        response = await self._request("POST", "/simulate/authorize", data)
        return self._parse_transaction(response)
