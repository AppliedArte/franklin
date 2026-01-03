"""Finance Tool - Banking, tax, and financial management."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from src.config import get_settings
from src.tools.base import Tool, ToolAction, ToolResult, ToolCategory, ApprovalLevel

settings = get_settings()


@dataclass
class BankAccount:
    """A connected bank account."""
    id: str
    institution: str
    name: str
    type: str  # checking, savings, credit, investment
    balance: Decimal
    currency: str = "USD"
    last_updated: datetime = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "institution": self.institution,
            "name": self.name,
            "type": self.type,
            "balance": f"${self.balance:,.2f}",
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }


@dataclass
class Transaction:
    """A financial transaction."""
    id: str
    account_id: str
    date: date
    description: str
    amount: Decimal
    category: Optional[str] = None
    merchant: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "description": self.description,
            "amount": f"${self.amount:,.2f}",
            "category": self.category,
        }


class FinanceTool(Tool):
    """Tool for financial management - banking, tax, payments."""

    name = "finance"
    description = "View accounts, track spending, manage taxes, and handle payments"
    category = ToolCategory.FINANCE
    version = "1.0.0"

    requires_auth = True
    auth_type = "oauth2"  # Plaid

    # Strict approval for financial actions
    cost_threshold_auto = Decimal("0")
    cost_threshold_notify = Decimal("100")

    def _register_actions(self) -> None:
        """Register finance actions."""
        # Read-only account actions
        self.register_action(ToolAction(
            name="list_accounts",
            description="List connected bank accounts and balances",
            parameters={
                "account_type": {"type": "string", "enum": ["all", "checking", "savings", "credit", "investment"]},
            },
            approval_level=ApprovalLevel.NONE,
        ))

        self.register_action(ToolAction(
            name="get_transactions",
            description="Get recent transactions for an account",
            parameters={
                "account_id": {"type": "string", "description": "Account ID"},
                "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                "category": {"type": "string", "description": "Filter by category"},
                "limit": {"type": "integer", "default": 50},
            },
            approval_level=ApprovalLevel.NONE,
        ))

        self.register_action(ToolAction(
            name="spending_summary",
            description="Get spending summary by category",
            parameters={
                "period": {"type": "string", "enum": ["week", "month", "quarter", "year"], "required": True},
                "account_id": {"type": "string", "description": "Specific account or all"},
            },
            approval_level=ApprovalLevel.NONE,
        ))

        # Tax-related actions
        self.register_action(ToolAction(
            name="tax_summary",
            description="Get tax-relevant summary for the year",
            parameters={
                "year": {"type": "integer", "description": "Tax year", "required": True},
            },
            approval_level=ApprovalLevel.NONE,
        ))

        self.register_action(ToolAction(
            name="estimate_taxes",
            description="Estimate taxes owed based on income and deductions",
            parameters={
                "year": {"type": "integer", "required": True},
                "include_projections": {"type": "boolean", "default": True},
            },
            approval_level=ApprovalLevel.NONE,
        ))

        self.register_action(ToolAction(
            name="prepare_tax_documents",
            description="Gather and organize documents for tax filing",
            parameters={
                "year": {"type": "integer", "required": True},
                "filing_status": {"type": "string", "enum": ["single", "married_joint", "married_separate", "head_of_household"]},
            },
            approval_level=ApprovalLevel.NOTIFY,  # Just organizing, not filing
        ))

        self.register_action(ToolAction(
            name="submit_tax_return",
            description="Submit tax return to IRS (via authorized e-file provider)",
            parameters={
                "year": {"type": "integer", "required": True},
                "provider": {"type": "string", "description": "E-file provider to use"},
            },
            approval_level=ApprovalLevel.STRICT,  # Highest approval for tax filing
        ))

        # Payment actions
        self.register_action(ToolAction(
            name="schedule_payment",
            description="Schedule a bill payment or transfer",
            parameters={
                "from_account": {"type": "string", "required": True},
                "to": {"type": "string", "description": "Payee or account", "required": True},
                "amount": {"type": "number", "required": True},
                "date": {"type": "string", "description": "Payment date (YYYY-MM-DD)", "required": True},
                "memo": {"type": "string"},
            },
            approval_level=ApprovalLevel.CONFIRM,
        ))

    async def execute(self, action: str, params: dict, user_id: UUID) -> ToolResult:
        """Execute a finance action."""
        if action == "list_accounts":
            return await self._list_accounts(params, user_id)
        elif action == "get_transactions":
            return await self._get_transactions(params, user_id)
        elif action == "spending_summary":
            return await self._spending_summary(params, user_id)
        elif action == "tax_summary":
            return await self._tax_summary(params, user_id)
        elif action == "estimate_taxes":
            return await self._estimate_taxes(params, user_id)
        elif action == "prepare_tax_documents":
            return await self._prepare_tax_documents(params, user_id)
        elif action == "submit_tax_return":
            return await self._submit_tax_return(params, user_id)
        elif action == "schedule_payment":
            return await self._schedule_payment(params, user_id)
        else:
            return ToolResult(success=False, error=f"Unknown action: {action}")

    async def _list_accounts(self, params: dict, user_id: UUID) -> ToolResult:
        """List connected accounts."""
        # TODO: Integrate with Plaid
        mock_accounts = [
            BankAccount(
                id="acc1",
                institution="Chase",
                name="Primary Checking",
                type="checking",
                balance=Decimal("15432.67"),
                last_updated=datetime.utcnow(),
            ),
            BankAccount(
                id="acc2",
                institution="Chase",
                name="Savings",
                type="savings",
                balance=Decimal("52891.23"),
                last_updated=datetime.utcnow(),
            ),
            BankAccount(
                id="acc3",
                institution="Fidelity",
                name="Brokerage",
                type="investment",
                balance=Decimal("248756.89"),
                last_updated=datetime.utcnow(),
            ),
            BankAccount(
                id="acc4",
                institution="Amex",
                name="Platinum Card",
                type="credit",
                balance=Decimal("-3421.50"),
                last_updated=datetime.utcnow(),
            ),
        ]

        account_type = params.get("account_type", "all")
        if account_type != "all":
            mock_accounts = [a for a in mock_accounts if a.type == account_type]

        total = sum(a.balance for a in mock_accounts)

        return ToolResult(
            success=True,
            data=[a.to_dict() for a in mock_accounts],
            summary=f"{len(mock_accounts)} accounts, net worth: ${total:,.2f}",
            metadata={"mock": True, "total_balance": float(total)},
        )

    async def _get_transactions(self, params: dict, user_id: UUID) -> ToolResult:
        """Get transactions."""
        mock_transactions = [
            Transaction(id="tx1", account_id="acc1", date=date(2024, 1, 2), description="Whole Foods", amount=Decimal("-127.43"), category="Groceries", merchant="Whole Foods"),
            Transaction(id="tx2", account_id="acc1", date=date(2024, 1, 2), description="Uber", amount=Decimal("-34.50"), category="Transport", merchant="Uber"),
            Transaction(id="tx3", account_id="acc1", date=date(2024, 1, 1), description="Salary Deposit", amount=Decimal("8500.00"), category="Income"),
            Transaction(id="tx4", account_id="acc1", date=date(2024, 1, 1), description="Netflix", amount=Decimal("-15.99"), category="Entertainment", merchant="Netflix"),
        ]

        return ToolResult(
            success=True,
            data=[t.to_dict() for t in mock_transactions],
            summary=f"{len(mock_transactions)} transactions",
            metadata={"mock": True},
        )

    async def _spending_summary(self, params: dict, user_id: UUID) -> ToolResult:
        """Get spending by category."""
        mock_summary = {
            "period": params["period"],
            "total_spent": "$4,523.45",
            "categories": [
                {"name": "Housing", "amount": "$2,100.00", "percent": 46},
                {"name": "Food", "amount": "$650.00", "percent": 14},
                {"name": "Transport", "amount": "$420.00", "percent": 9},
                {"name": "Entertainment", "amount": "$280.00", "percent": 6},
                {"name": "Shopping", "amount": "$573.45", "percent": 13},
                {"name": "Other", "amount": "$500.00", "percent": 11},
            ],
        }

        return ToolResult(
            success=True,
            data=mock_summary,
            summary=f"Spent {mock_summary['total_spent']} this {params['period']}",
            metadata={"mock": True},
        )

    async def _tax_summary(self, params: dict, user_id: UUID) -> ToolResult:
        """Get tax-relevant data."""
        year = params["year"]
        mock_summary = {
            "year": year,
            "gross_income": "$156,000.00",
            "w2_income": "$145,000.00",
            "investment_income": "$11,000.00",
            "deductions": {
                "standard": "$13,850.00",
                "itemized_potential": "$18,500.00",
                "recommended": "itemized",
            },
            "estimated_tax_liability": "$28,750.00",
            "taxes_paid_ytd": "$32,100.00",
            "estimated_refund": "$3,350.00",
        }

        return ToolResult(
            success=True,
            data=mock_summary,
            summary=f"{year} tax summary: estimated refund of {mock_summary['estimated_refund']}",
            metadata={"mock": True},
        )

    async def _estimate_taxes(self, params: dict, user_id: UUID) -> ToolResult:
        """Estimate tax liability."""
        return ToolResult(
            success=True,
            data={
                "federal": "$24,500.00",
                "state": "$4,250.00",
                "total": "$28,750.00",
                "effective_rate": "18.4%",
                "marginal_rate": "24%",
            },
            summary="Estimated total tax liability: $28,750",
            metadata={"mock": True},
        )

    async def _prepare_tax_documents(self, params: dict, user_id: UUID) -> ToolResult:
        """Prepare tax documents."""
        documents = [
            {"name": "W-2 (Employer)", "status": "received", "source": "Acme Corp"},
            {"name": "1099-INT (Bank Interest)", "status": "received", "source": "Chase"},
            {"name": "1099-DIV (Dividends)", "status": "received", "source": "Fidelity"},
            {"name": "1098 (Mortgage Interest)", "status": "pending", "source": "Wells Fargo"},
            {"name": "Charitable Donations", "status": "needs_input", "source": "Manual"},
        ]

        return ToolResult(
            success=True,
            data={"documents": documents, "completion": "80%"},
            summary="Tax documents 80% complete - need mortgage 1098 and charitable receipts",
            metadata={"mock": True},
        )

    async def _submit_tax_return(self, params: dict, user_id: UUID) -> ToolResult:
        """Submit tax return - requires strict approval."""
        # This would integrate with e-file providers
        return ToolResult(
            success=False,
            error="Tax submission requires strict approval and e-file provider setup",
            metadata={"approval_required": True, "level": "strict"},
        )

    async def _schedule_payment(self, params: dict, user_id: UUID) -> ToolResult:
        """Schedule a payment."""
        return ToolResult(
            success=True,
            data={
                "from": params["from_account"],
                "to": params["to"],
                "amount": f"${params['amount']:,.2f}",
                "date": params["date"],
            },
            summary=f"Payment of ${params['amount']:,.2f} scheduled for {params['date']}",
            metadata={"mock": True, "approval_required": True},
        )
