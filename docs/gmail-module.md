# Gmail Module

The Gmail module enables Franklin to read, analyze, and manage emails with AI-powered importance scoring and spam detection.

---

## Overview

| Feature | Description |
|---------|-------------|
| **OAuth Integration** | Extends existing Google OAuth with Gmail scopes |
| **AI Analysis** | Claude-powered importance scoring and spam detection |
| **Full Actions** | Archive, trash, label, mark read/unread, move to spam |
| **On-Demand** | Analyzes emails when user asks |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Gmail Tool                              │
│                  src/tools/gmail.py                          │
├─────────────────────────────────────────────────────────────┤
│  Actions: analyze_inbox, list_emails, read_email,           │
│           get_important, get_spam_candidates,               │
│           archive, trash, move_to_spam, label,              │
│           mark_read, mark_unread, bulk_cleanup              │
└──────────────────────────┬──────────────────────────────────┘
                           │
           ┌───────────────┴───────────────┐
           │                               │
           ▼                               ▼
┌─────────────────────┐       ┌─────────────────────┐
│   Gmail Service     │       │   Gmail Analyzer    │
│ src/services/       │       │ src/services/       │
│ gmail.py            │       │ gmail_analyzer.py   │
├─────────────────────┤       ├─────────────────────┤
│ Gmail API wrapper   │       │ Claude AI analysis  │
│ - list_messages     │       │ - importance score  │
│ - get_message       │       │ - spam detection    │
│ - modify_message    │       │ - inbox summary     │
│ - trash/archive     │       │                     │
└──────────┬──────────┘       └──────────┬──────────┘
           │                             │
           ▼                             ▼
┌─────────────────────┐       ┌─────────────────────┐
│   Google OAuth      │       │   Anthropic API     │
│   (Gmail scopes)    │       │   (Claude)          │
└─────────────────────┘       └─────────────────────┘
```

---

## Setup

### 1. Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the **Gmail API** for your project
3. Add OAuth consent screen scopes:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.modify`
   - `https://www.googleapis.com/auth/gmail.labels`

### 2. Environment Variables

These should already be configured for Google Calendar OAuth:

```bash
GOOGLE_OAUTH_CLIENT_ID=your_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/oauth/google/callback
OAUTH_ENCRYPTION_KEY=your_fernet_key  # For token encryption
```

### 3. User Authorization

Users can connect Gmail via:

```
GET /oauth/google/gmail/authorize?user_id=<user_id>
```

Or connect both Calendar and Gmail:

```
GET /oauth/google/all/authorize?user_id=<user_id>
```

---

## API Reference

### OAuth Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/oauth/google/gmail/authorize` | GET | Start Gmail OAuth flow |
| `/oauth/google/all/authorize` | GET | Start Calendar + Gmail OAuth |
| `/oauth/google/status` | GET | Check OAuth connection status |
| `/oauth/google/revoke` | DELETE | Disconnect Google OAuth |

### Tool Actions

#### Read-Only Actions (Auto-approved)

##### `analyze_inbox`
Analyze recent emails for importance and spam.

**Parameters:**
- `days` (int, default: 30): Days to look back
- `max_emails` (int, default: 100): Maximum emails to analyze

**Returns:**
```json
{
  "total_analyzed": 85,
  "important_count": 12,
  "spam_candidates_count": 8,
  "unread_count": 23,
  "summary": "You have 85 emails from the last 30 days...",
  "important_emails": [...],
  "spam_candidates": [...]
}
```

##### `list_emails`
List emails with optional filters.

**Parameters:**
- `query` (string): Gmail search query (e.g., "from:user@example.com")
- `label` (string): Filter by label (e.g., "INBOX", "STARRED")
- `unread_only` (bool): Only unread emails
- `days` (int): Emails from last N days
- `limit` (int, default: 20): Maximum results

##### `read_email`
Read full content of an email.

**Parameters:**
- `email_id` (string, required): Gmail message ID

##### `get_important`
Get AI-identified important emails.

**Parameters:**
- `threshold` (float, default: 0.7): Importance score threshold (0-1)
- `days` (int, default: 7): Days to look back
- `max_emails` (int, default: 50): Maximum to analyze

##### `get_spam_candidates`
Get emails identified as potential spam.

**Parameters:**
- `threshold` (float, default: 0.6): Spam probability threshold (0-1)
- `days` (int, default: 30): Days to analyze
- `max_emails` (int, default: 100): Maximum to analyze

#### Write Actions (Require Confirmation)

##### `archive`
Archive email(s).

**Parameters:**
- `email_ids` (array, required): List of email IDs to archive

##### `trash`
Move email(s) to trash.

**Parameters:**
- `email_ids` (array, required): List of email IDs

##### `move_to_spam`
Mark as spam and move to junk folder.

**Parameters:**
- `email_ids` (array, required): List of email IDs

##### `label`
Add/remove labels from emails.

**Parameters:**
- `email_ids` (array, required): List of email IDs
- `add_labels` (array): Labels to add
- `remove_labels` (array): Labels to remove

#### Notify-Level Actions

##### `mark_read` / `mark_unread`
Mark email(s) as read or unread.

**Parameters:**
- `email_ids` (array, required): List of email IDs

#### Strict Approval Actions

##### `bulk_cleanup`
Bulk cleanup based on AI spam detection.

**Parameters:**
- `action` (string, required): "trash", "spam", or "archive"
- `spam_threshold` (float, default: 0.8): Higher = more conservative
- `days` (int, default: 30): Days to analyze
- `dry_run` (bool, default: true): Preview without acting

---

## AI Analysis

### Importance Scoring

Emails are scored 0-1 based on:

**High Importance (0.7+):**
- Direct messages from real people
- Financial/investment discussions
- Time-sensitive requests
- Client communications
- Meeting requests
- Legal/compliance matters

**Low Importance:**
- Marketing/promotional emails
- Newsletters
- Automated notifications
- Social media updates

### Spam Detection

Spam probability (0-1) based on:

**Spam Indicators:**
- Unsolicited commercial content
- Phishing attempts
- Fake urgency tactics
- Misspelled sender domains
- Generic greetings ("Dear Customer")
- Suspicious links

**Legitimate Indicators:**
- From known contacts
- Personalized content
- Expected notifications
- Proper unsubscribe mechanisms

---

## Usage Examples

### Franklin Conversation

```
User: "Check my emails for anything important"

Franklin: "I shall review your correspondence forthwith, Master.

          I've analyzed 85 emails from the past month:
          - 12 require your attention
          - 8 appear to be unsolicited rubbish

          Most urgent:
          1. John Smith: Q1 Portfolio Review Request (action needed)
          2. Bank of America: Wire Transfer Confirmation
          3. Sarah Chen: Investment Opportunity Discussion

          Shall I provide more details on any of these?"
```

```
User: "Move the spam to junk"

Franklin: "I've identified 8 emails as likely spam:
          - Marketing Newsletter (spam probability: 92%)
          - "You've Won!" Notification (spam probability: 95%)
          - ...

          Shall I move these to your spam folder?"

User: "Yes"

Franklin: "Done. I've moved 8 emails to your spam folder."
```

---

## Data Models

### GmailMessage

```python
@dataclass
class GmailMessage:
    id: str
    thread_id: str
    subject: str
    sender: str
    sender_email: str
    to: list[str]
    date: datetime
    snippet: str
    body_text: Optional[str]
    body_html: Optional[str]
    labels: list[str]
    is_read: bool
    is_starred: bool
    is_important: bool
    has_attachments: bool

    # AI-computed fields
    importance_score: Optional[float]
    spam_probability: Optional[float]
    category: Optional[str]
```

### EmailAnalysis

```python
@dataclass
class EmailAnalysis:
    message_id: str
    importance_score: float      # 0-1
    importance_reason: str       # Brief explanation
    spam_probability: float      # 0-1
    spam_signals: list[str]      # Red flags detected
    category: str                # primary, social, promotions, etc.
    action_required: bool
    suggested_action: Optional[str]  # respond, archive, schedule
    summary: str                 # 1-2 sentence summary
```

---

## Files

| File | Description |
|------|-------------|
| `src/api/oauth.py` | Gmail OAuth scopes and endpoints |
| `src/services/gmail.py` | Gmail API service wrapper |
| `src/services/gmail_analyzer.py` | AI-powered email analysis |
| `src/tools/gmail.py` | Gmail tool for agentic use |
| `src/tools/registry.py` | Tool registration |

---

## Approval Levels

| Action | Level | Description |
|--------|-------|-------------|
| analyze_inbox | NONE | Auto-approved (read-only) |
| list_emails | NONE | Auto-approved |
| read_email | NONE | Auto-approved |
| get_important | NONE | Auto-approved |
| get_spam_candidates | NONE | Auto-approved |
| archive | CONFIRM | Requires user confirmation |
| trash | CONFIRM | Requires user confirmation |
| move_to_spam | CONFIRM | Requires user confirmation |
| label | CONFIRM | Requires user confirmation |
| mark_read | NOTIFY | Execute and notify user |
| mark_unread | NOTIFY | Execute and notify user |
| bulk_cleanup | STRICT | Requires verification |

---

## Rate Limits

Gmail API quotas:
- 250 quota units per user per second
- `messages.list`: 5 units
- `messages.get`: 5 units
- `messages.modify`: 5 units

The service handles rate limiting gracefully with appropriate error messages.

---

## Security

- **OAuth tokens**: Encrypted at rest with Fernet
- **Scopes**: Minimum required (readonly + modify + labels)
- **No permanent storage**: Email content is not stored in database
- **Audit trail**: All write actions are logged
