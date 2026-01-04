# Franklin Documentation

Technical documentation for the Franklin AI Wealth Advisor.

## Modules

| Module | Description |
|--------|-------------|
| [Payments](payments.md) | Autonomous spending with spending rules |
| [Tools](tools.md) | All available tools (travel, calendar, email, etc.) |
| [Adapters](adapters.md) | External service integrations |

## Quick Links

- [Main README](../README.md) - Project overview
- [Deployment Guide](../DEPLOYMENT.md) - Production deployment
- [Environment Variables](../README.md#environment-variables)

## Architecture

```
User Message
     │
     ▼
┌─────────────────┐
│  Orchestrator   │ ← Routes to appropriate agent
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌───────┐
│Profile│ │Advisor│
│Builder│ │ Agent │
└───────┘ └───┬───┘
              │
              ▼
       ┌──────────────┐
       │    Tools     │ ← Payments, Travel, Calendar, etc.
       └──────────────┘
              │
              ▼
       ┌──────────────┐
       │   Adapters   │ ← Privacy.com, Kiwi, Google, etc.
       └──────────────┘
```

## Key Concepts

### Spending Rules
Pre-defined limits that allow Franklin to spend autonomously:
- `auto_approve_under` - Silent execution
- `notify_only_under` - Execute + notify
- Above threshold - Ask for approval

### Approval Levels
- `NONE` - Read-only operations
- `NOTIFY` - Execute and inform
- `CONFIRM` - Ask before executing
- `STRICT` - Require verification

### Tool Registry
All tools are registered at startup:
```python
from src.tools.registry import register_all_tools
register_all_tools()
```
