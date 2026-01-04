"""Payments Tool - Autonomous spending and purchase execution.

This tool enables Franklin to make purchases on behalf of the user
within pre-defined spending rules. The user sets up rules once,
and Franklin can then execute purchases autonomously.

Security model:
1. Virtual cards with spending limits (failsafe at provider level)
2. User-defined spending rules per category
3. Auto-approve under threshold, notify under higher threshold, ask above
4. Full audit trail of all purchases
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.db.database import get_session
from src.db.models import (
    SpendingRule, PaymentMethod, Purchase,
    PurchaseStatus, PurchaseCategory, PaymentMethodType
)
from src.tools.base import Tool, ToolAction, ToolResult, ToolCategory, ApprovalLevel

settings = get_settings()


@dataclass
class SpendingCheck:
    """Result of checking if a purchase can be made."""
    allowed: bool
    approval_level: ApprovalLevel
    reason: str
    remaining_budget: Optional[float] = None


class PaymentsTool(Tool):
    """Tool for autonomous spending and purchase execution.

    This tool allows Franklin to:
    1. View and manage spending rules
    2. Check if purchases are within limits
    3. Execute purchases using stored payment methods
    4. Track purchase history
    """

    name = "payments"
    description = "Manage spending rules and execute purchases autonomously"
    category = ToolCategory.FINANCE
    version = "1.0.0"

    requires_auth = False  # Payment methods are stored, no external OAuth needed
    auth_type = None

    default_approval_level = ApprovalLevel.CONFIRM

    def _register_actions(self) -> None:
        """Register payments actions."""

        # ===== Spending Rules Management =====
        self.register_action(ToolAction(
            name="get_spending_rules",
            description="Get user's spending rules and limits",
            parameters={
                "category": {
                    "type": "string",
                    "description": "Filter by category (flights, hotels, etc.) or 'all'",
                },
            },
            approval_level=ApprovalLevel.NONE,  # Read-only
        ))

        self.register_action(ToolAction(
            name="set_spending_rule",
            description="Create or update a spending rule for a category",
            parameters={
                "category": {
                    "type": "string",
                    "enum": ["flights", "hotels", "transport", "restaurants",
                             "subscriptions", "shopping", "entertainment",
                             "utilities", "general", "all"],
                    "required": True,
                },
                "max_per_transaction": {
                    "type": "number",
                    "description": "Maximum amount per purchase",
                },
                "max_daily": {
                    "type": "number",
                    "description": "Maximum daily spending",
                },
                "max_monthly": {
                    "type": "number",
                    "description": "Maximum monthly spending",
                },
                "auto_approve_under": {
                    "type": "number",
                    "description": "Auto-approve purchases under this amount",
                },
                "notify_only_under": {
                    "type": "number",
                    "description": "Just notify (no approval needed) under this amount",
                },
                "preferences": {
                    "type": "object",
                    "description": "Category-specific preferences (e.g., airline class, hotel stars)",
                },
            },
            approval_level=ApprovalLevel.CONFIRM,  # Changing rules needs approval
        ))

        # ===== Payment Methods =====
        self.register_action(ToolAction(
            name="list_payment_methods",
            description="List stored payment methods",
            parameters={},
            approval_level=ApprovalLevel.NONE,
        ))

        self.register_action(ToolAction(
            name="add_payment_method",
            description="Add a new payment method (virtual card recommended)",
            parameters={
                "nickname": {
                    "type": "string",
                    "description": "Friendly name for this payment method",
                    "required": True,
                },
                "method_type": {
                    "type": "string",
                    "enum": ["virtual_card", "debit_card", "credit_card"],
                    "required": True,
                },
                "provider": {
                    "type": "string",
                    "description": "Provider (privacy, lithic, manual)",
                    "required": True,
                },
                "card_number": {
                    "type": "string",
                    "description": "Card number",
                    "required": True,
                },
                "expiry": {
                    "type": "string",
                    "description": "Expiry date (MM/YY)",
                    "required": True,
                },
                "cvv": {
                    "type": "string",
                    "description": "CVV/CVC",
                    "required": True,
                },
                "spending_limit": {
                    "type": "number",
                    "description": "Card spending limit",
                },
                "billing_name": {
                    "type": "string",
                    "description": "Name on card",
                },
                "billing_address": {
                    "type": "object",
                    "description": "Billing address",
                },
                "set_as_default": {
                    "type": "boolean",
                    "description": "Set as default payment method",
                },
            },
            approval_level=ApprovalLevel.STRICT,  # Adding payment methods is sensitive
        ))

        # ===== Purchase Execution =====
        self.register_action(ToolAction(
            name="check_purchase",
            description="Check if a purchase is allowed within spending rules",
            parameters={
                "category": {
                    "type": "string",
                    "required": True,
                },
                "amount": {
                    "type": "number",
                    "required": True,
                },
                "merchant": {
                    "type": "string",
                    "required": True,
                },
            },
            approval_level=ApprovalLevel.NONE,  # Just checking, no action
        ))

        self.register_action(ToolAction(
            name="execute_purchase",
            description="Execute a purchase (book flight, hotel, etc.)",
            parameters={
                "category": {
                    "type": "string",
                    "required": True,
                },
                "amount": {
                    "type": "number",
                    "required": True,
                },
                "currency": {
                    "type": "string",
                    "default": "USD",
                },
                "merchant": {
                    "type": "string",
                    "required": True,
                },
                "description": {
                    "type": "string",
                    "required": True,
                },
                "purchase_data": {
                    "type": "object",
                    "description": "Details of what's being purchased",
                },
                "payment_method_id": {
                    "type": "string",
                    "description": "Specific payment method to use (uses default if not specified)",
                },
                "original_request": {
                    "type": "string",
                    "description": "User's original request that led to this purchase",
                },
            },
            # Approval level is dynamic based on amount and rules
            approval_level=ApprovalLevel.CONFIRM,
        ))

        # ===== Purchase History =====
        self.register_action(ToolAction(
            name="purchase_history",
            description="Get purchase history",
            parameters={
                "category": {
                    "type": "string",
                    "description": "Filter by category",
                },
                "status": {
                    "type": "string",
                    "description": "Filter by status",
                },
                "limit": {
                    "type": "integer",
                    "default": 20,
                },
                "days": {
                    "type": "integer",
                    "description": "Look back this many days",
                    "default": 30,
                },
            },
            approval_level=ApprovalLevel.NONE,
        ))

        self.register_action(ToolAction(
            name="spending_summary",
            description="Get spending summary by category and time period",
            parameters={
                "period": {
                    "type": "string",
                    "enum": ["day", "week", "month", "year"],
                    "default": "month",
                },
            },
            approval_level=ApprovalLevel.NONE,
        ))

    async def execute(self, action: str, params: dict, user_id: UUID) -> ToolResult:
        """Execute a payments action."""
        actions = {
            "get_spending_rules": self._get_spending_rules,
            "set_spending_rule": self._set_spending_rule,
            "list_payment_methods": self._list_payment_methods,
            "add_payment_method": self._add_payment_method,
            "check_purchase": self._check_purchase,
            "execute_purchase": self._execute_purchase,
            "purchase_history": self._purchase_history,
            "spending_summary": self._spending_summary,
        }

        handler = actions.get(action)
        if not handler:
            return ToolResult(success=False, error=f"Unknown action: {action}")

        return await handler(params, user_id)

    # =========================================================================
    # Spending Rules
    # =========================================================================

    async def _get_spending_rules(self, params: dict, user_id: UUID) -> ToolResult:
        """Get user's spending rules."""
        async with get_session() as session:
            query = select(SpendingRule).where(
                SpendingRule.user_id == str(user_id),
                SpendingRule.is_active == True
            )

            category = params.get("category")
            if category and category != "all":
                query = query.where(SpendingRule.category == category)

            result = await session.execute(query)
            rules = result.scalars().all()

            if not rules:
                return ToolResult(
                    success=True,
                    data={"rules": [], "using_defaults": True},
                    summary="No custom spending rules set. Using defaults: ask approval for all purchases.",
                )

            rules_data = [{
                "id": r.id,
                "category": r.category,
                "max_per_transaction": r.max_per_transaction,
                "max_daily": r.max_daily,
                "max_monthly": r.max_monthly,
                "auto_approve_under": r.auto_approve_under,
                "notify_only_under": r.notify_only_under,
                "preferences": r.preferences,
            } for r in rules]

            return ToolResult(
                success=True,
                data={"rules": rules_data},
                summary=f"{len(rules)} spending rule(s) configured",
            )

    async def _set_spending_rule(self, params: dict, user_id: UUID) -> ToolResult:
        """Create or update a spending rule."""
        category = params["category"]

        async with get_session() as session:
            result = await session.execute(
                select(SpendingRule).where(
                    SpendingRule.user_id == str(user_id),
                    SpendingRule.category == category
                )
            )
            rule = result.scalar_one_or_none()

            if rule:
                for key in ["max_per_transaction", "max_daily", "max_monthly",
                           "auto_approve_under", "notify_only_under", "preferences"]:
                    if key in params:
                        setattr(rule, key, params[key])
                rule.is_active = True
            else:
                rule = SpendingRule(
                    id=str(uuid4()),
                    user_id=str(user_id),
                    category=category,
                    max_per_transaction=params.get("max_per_transaction", 500.0),
                    max_daily=params.get("max_daily"),
                    max_monthly=params.get("max_monthly"),
                    auto_approve_under=params.get("auto_approve_under", 100.0),
                    notify_only_under=params.get("notify_only_under", 500.0),
                    preferences=params.get("preferences"),
                )
                session.add(rule)

            await session.commit()

            return ToolResult(
                success=True,
                data={
                    "category": category,
                    "auto_approve_under": rule.auto_approve_under,
                    "notify_only_under": rule.notify_only_under,
                    "max_per_transaction": rule.max_per_transaction,
                },
                summary=f"Spending rule for '{category}' saved. Auto-approve under ${rule.auto_approve_under:.2f}",
            )

    # =========================================================================
    # Payment Methods
    # =========================================================================

    async def _list_payment_methods(self, params: dict, user_id: UUID) -> ToolResult:
        """List user's payment methods."""
        async with get_session() as session:
            result = await session.execute(
                select(PaymentMethod).where(
                    PaymentMethod.user_id == str(user_id),
                    PaymentMethod.is_active == True
                )
            )
            methods = result.scalars().all()

            if not methods:
                return ToolResult(
                    success=True,
                    data={"methods": []},
                    summary="No payment methods configured. Add a virtual card to enable autonomous purchases.",
                )

            methods_data = [{
                "id": m.id,
                "nickname": m.nickname,
                "type": m.method_type,
                "provider": m.provider,
                "last_four": "****",
                "spending_limit": m.spending_limit,
                "amount_spent": m.amount_spent,
                "is_default": m.is_default,
            } for m in methods]

            return ToolResult(
                success=True,
                data={"methods": methods_data},
                summary=f"{len(methods)} payment method(s) available",
            )

    async def _add_payment_method(self, params: dict, user_id: UUID) -> ToolResult:
        """Add a new payment method."""
        from cryptography.fernet import Fernet

        if not settings.oauth_encryption_key:
            return ToolResult(
                success=False,
                error="Encryption not configured. Cannot store payment methods securely.",
            )

        fernet = Fernet(settings.oauth_encryption_key.encode())

        async with get_session() as session:
            # If setting as default, unset other defaults
            if params.get("set_as_default", False):
                existing = await session.execute(
                    select(PaymentMethod).where(
                        PaymentMethod.user_id == str(user_id),
                        PaymentMethod.is_default == True
                    )
                )
                for pm in existing.scalars():
                    pm.is_default = False

            method = PaymentMethod(
                id=str(uuid4()),
                user_id=str(user_id),
                nickname=params["nickname"],
                method_type=params["method_type"],
                provider=params["provider"],
                card_number_encrypted=fernet.encrypt(params["card_number"].encode()).decode(),
                expiry_encrypted=fernet.encrypt(params["expiry"].encode()).decode(),
                cvv_encrypted=fernet.encrypt(params["cvv"].encode()).decode(),
                spending_limit=params.get("spending_limit"),
                billing_name=params.get("billing_name"),
                billing_address=params.get("billing_address"),
                is_default=params.get("set_as_default", False),
            )
            session.add(method)
            await session.commit()

            return ToolResult(
                success=True,
                data={"id": method.id, "nickname": method.nickname, "type": method.method_type},
                summary=f"Payment method '{method.nickname}' added successfully",
            )

    # =========================================================================
    # Purchase Checking & Execution
    # =========================================================================

    async def _check_spending_limits(
        self, session: AsyncSession, user_id: str, category: str, amount: float
    ) -> SpendingCheck:
        """Check if a purchase is within spending limits."""
        result = await session.execute(
            select(SpendingRule).where(
                SpendingRule.user_id == user_id,
                SpendingRule.category.in_([category, "all"]),
                SpendingRule.is_active == True
            ).order_by(SpendingRule.category.desc())
        )
        rule = result.scalars().first()

        if not rule:
            return SpendingCheck(
                allowed=True,
                approval_level=ApprovalLevel.CONFIRM,
                reason="No spending rule for this category. Approval required.",
            )

        # Check per-transaction limit
        if amount > rule.max_per_transaction:
            return SpendingCheck(
                allowed=False,
                approval_level=ApprovalLevel.STRICT,
                reason=f"Exceeds max per transaction (${rule.max_per_transaction:.2f})",
            )

        # Check daily limit
        if rule.max_daily:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            daily_result = await session.execute(
                select(func.sum(Purchase.amount)).where(
                    Purchase.user_id == user_id,
                    Purchase.category == category,
                    Purchase.status.in_(["completed", "processing"]),
                    Purchase.created_at >= today_start
                )
            )
            daily_spent = daily_result.scalar() or 0

            if daily_spent + amount > rule.max_daily:
                return SpendingCheck(
                    allowed=False,
                    approval_level=ApprovalLevel.STRICT,
                    reason=f"Would exceed daily limit (${rule.max_daily:.2f}). Already spent ${daily_spent:.2f} today.",
                    remaining_budget=rule.max_daily - daily_spent,
                )

        # Check monthly limit
        if rule.max_monthly:
            month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            monthly_result = await session.execute(
                select(func.sum(Purchase.amount)).where(
                    Purchase.user_id == user_id,
                    Purchase.category == category,
                    Purchase.status.in_(["completed", "processing"]),
                    Purchase.created_at >= month_start
                )
            )
            monthly_spent = monthly_result.scalar() or 0

            if monthly_spent + amount > rule.max_monthly:
                return SpendingCheck(
                    allowed=False,
                    approval_level=ApprovalLevel.STRICT,
                    reason=f"Would exceed monthly limit (${rule.max_monthly:.2f}). Already spent ${monthly_spent:.2f} this month.",
                    remaining_budget=rule.max_monthly - monthly_spent,
                )

        # Determine approval level based on amount
        if amount <= rule.auto_approve_under:
            approval_level = ApprovalLevel.NONE
            reason = f"Under auto-approve threshold (${rule.auto_approve_under:.2f})"
        elif amount <= rule.notify_only_under:
            approval_level = ApprovalLevel.NOTIFY
            reason = f"Under notify-only threshold (${rule.notify_only_under:.2f})"
        else:
            approval_level = ApprovalLevel.CONFIRM
            reason = "Above notify threshold, approval required"

        return SpendingCheck(allowed=True, approval_level=approval_level, reason=reason)

    async def _check_purchase(self, params: dict, user_id: UUID) -> ToolResult:
        """Check if a purchase can be made."""
        async with get_session() as session:
            check = await self._check_spending_limits(
                session,
                str(user_id),
                params["category"],
                params["amount"]
            )

            return ToolResult(
                success=True,
                data={
                    "allowed": check.allowed,
                    "approval_level": check.approval_level.value,
                    "reason": check.reason,
                    "remaining_budget": check.remaining_budget,
                },
                summary=f"{'✓ Allowed' if check.allowed else '✗ Blocked'}: {check.reason}",
            )

    async def _execute_purchase(self, params: dict, user_id: UUID) -> ToolResult:
        """Execute a purchase."""
        async with get_session() as session:
            # First check spending limits
            check = await self._check_spending_limits(
                session,
                str(user_id),
                params["category"],
                params["amount"]
            )

            if not check.allowed:
                return ToolResult(
                    success=False,
                    error=check.reason,
                    metadata={"approval_level": check.approval_level.value},
                )

            # Get payment method
            payment_method_id = params.get("payment_method_id")
            if payment_method_id:
                pm_result = await session.execute(
                    select(PaymentMethod).where(
                        PaymentMethod.id == payment_method_id,
                        PaymentMethod.user_id == str(user_id),
                        PaymentMethod.is_active == True
                    )
                )
            else:
                # Get default payment method
                pm_result = await session.execute(
                    select(PaymentMethod).where(
                        PaymentMethod.user_id == str(user_id),
                        PaymentMethod.is_default == True,
                        PaymentMethod.is_active == True
                    )
                )
            payment_method = pm_result.scalar_one_or_none()

            if not payment_method:
                return ToolResult(
                    success=False,
                    error="No payment method available. Please add a payment method first.",
                )

            # Check card spending limit
            if payment_method.spending_limit:
                if payment_method.amount_spent + params["amount"] > payment_method.spending_limit:
                    return ToolResult(
                        success=False,
                        error=f"Would exceed card spending limit (${payment_method.spending_limit:.2f})",
                    )

            # Create purchase record
            purchase = Purchase(
                id=str(uuid4()),
                user_id=str(user_id),
                payment_method_id=payment_method.id,
                category=params["category"],
                merchant=params["merchant"],
                description=params["description"],
                amount=params["amount"],
                currency=params.get("currency", "USD"),
                status=PurchaseStatus.PROCESSING.value,
                approval_required=check.approval_level != ApprovalLevel.NONE,
                approved_at=datetime.utcnow() if check.approval_level == ApprovalLevel.NONE else None,
                approval_method="auto" if check.approval_level == ApprovalLevel.NONE else None,
                purchase_data=params.get("purchase_data"),
                original_request=params.get("original_request"),
            )
            session.add(purchase)

            # Update payment method spend tracking
            payment_method.amount_spent += params["amount"]
            payment_method.last_used_at = datetime.utcnow()

            await session.commit()

            # In a real implementation, this would:
            # 1. Use the card details to make the actual purchase
            # 2. Integrate with booking APIs (Duffel for flights, etc.)
            # 3. Handle 3DS authentication if needed
            # 4. Update purchase status based on result

            return ToolResult(
                success=True,
                data={
                    "purchase_id": purchase.id,
                    "status": purchase.status,
                    "amount": f"${params['amount']:.2f}",
                    "merchant": params["merchant"],
                    "approval_level": check.approval_level.value,
                },
                summary=f"Purchase of ${params['amount']:.2f} at {params['merchant']} initiated",
                metadata={
                    "approval_level": check.approval_level.value,
                    "purchase_id": purchase.id,
                },
            )

    # =========================================================================
    # Purchase History & Analytics
    # =========================================================================

    async def _purchase_history(self, params: dict, user_id: UUID) -> ToolResult:
        """Get purchase history."""
        async with get_session() as session:
            query = select(Purchase).where(Purchase.user_id == str(user_id))

            if params.get("category"):
                query = query.where(Purchase.category == params["category"])
            if params.get("status"):
                query = query.where(Purchase.status == params["status"])

            days = params.get("days", 30)
            query = query.where(Purchase.created_at >= datetime.utcnow() - timedelta(days=days))
            query = query.order_by(Purchase.created_at.desc()).limit(params.get("limit", 20))

            result = await session.execute(query)
            purchases = result.scalars().all()

            purchases_data = [{
                "id": p.id,
                "date": p.created_at.isoformat(),
                "category": p.category,
                "merchant": p.merchant,
                "amount": f"${p.amount:.2f}",
                "status": p.status,
                "description": p.description[:100] if p.description else None,
            } for p in purchases]

            total = sum(p.amount for p in purchases if p.status == "completed")

            return ToolResult(
                success=True,
                data={"purchases": purchases_data, "total_completed": f"${total:.2f}"},
                summary=f"{len(purchases)} purchases in last {days} days, ${total:.2f} completed",
            )

    async def _spending_summary(self, params: dict, user_id: UUID) -> ToolResult:
        """Get spending summary."""
        period = params.get("period", "month")
        now = datetime.utcnow()

        # Calculate date range
        period_starts = {
            "day": now.replace(hour=0, minute=0, second=0, microsecond=0),
            "week": (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0),
            "month": now.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
            "year": now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0),
        }
        start = period_starts.get(period, now - timedelta(days=30))

        async with get_session() as session:
            result = await session.execute(
                select(
                    Purchase.category,
                    func.sum(Purchase.amount).label("total"),
                    func.count(Purchase.id).label("count")
                ).where(
                    Purchase.user_id == str(user_id),
                    Purchase.status == "completed",
                    Purchase.created_at >= start
                ).group_by(Purchase.category)
            )

            by_category = []
            grand_total = 0
            for row in result:
                by_category.append({
                    "category": row.category,
                    "total": f"${row.total:.2f}",
                    "count": row.count,
                })
                grand_total += row.total

            return ToolResult(
                success=True,
                data={
                    "period": period,
                    "start_date": start.isoformat(),
                    "by_category": by_category,
                    "grand_total": f"${grand_total:.2f}",
                },
                summary=f"Spent ${grand_total:.2f} this {period} across {len(by_category)} categories",
            )

    def get_approval_level(
        self, action: str, estimated_cost: Optional[Decimal] = None
    ) -> ApprovalLevel:
        """Override to provide dynamic approval based on spending rules.

        Note: The actual check happens in execute_purchase which queries the DB.
        This provides a default that gets refined at execution time.
        """
        tool_action = self.get_action(action)
        if tool_action:
            return tool_action.approval_level
        return self.default_approval_level
