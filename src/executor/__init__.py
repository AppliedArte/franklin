"""Franklin Executor - Action execution with approval gates."""

from src.executor.executor import Executor, ExecutionResult
from src.executor.approval import ApprovalManager, PendingApproval, ApprovalStatus

__all__ = [
    "Executor",
    "ExecutionResult",
    "ApprovalManager",
    "PendingApproval",
    "ApprovalStatus",
]
