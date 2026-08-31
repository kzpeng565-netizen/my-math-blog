# Issue-feedback backlog

The issue-feedback system is a lightweight ops inbox for problems the user notices while using the web UI or behavior advisor.

## Data location

```text
/home/conrad/workspace/activitywatch-advisor/data/issue_feedback/
├─ raw/YYYY-MM-DD/<issue_id>.json
├─ daily/YYYY-MM-DD.md
└─ UNREVIEWED.md
```

## API

```text
POST /api/issue-feedback
GET  /api/issue-feedback/recent
```

The API is available only after Next Action web login.

## Issue fields

```json
{
  "issue_id": "20260730-103012-a1b2c3",
  "created_at": "2026-07-30T10:30:12+08:00",
  "category": "ai_suggestion_quality",
  "severity": "medium",
  "message": "It treated one Pomodoro as 25 minutes.",
  "page": "next_action",
  "suggestion_id": "optional",
  "report_path": "optional",
  "user_agent": "redacted browser string",
  "status": "open"
}
```

Allowed categories:

```text
ai_suggestion_quality
data_wrong_or_missing
web_ui
notification
rule_mismatch
security_or_access
docs_or_handoff
other
```

Allowed severities:

```text
low
medium
high
blocking
```

## Processing workflow

When the user asks to process issues:

1. Read `UNREVIEWED.md`.
2. Read only the raw JSON for issues you are actively handling.
3. Classify each issue and decide whether it needs code, rules, docs, data repair, or no action.
4. Fix in the smallest scope.
5. Run tests and verify service behavior.
6. Mark issue status as resolved only after verification. If no code change is needed, record the decision.
7. Update handoff docs through `references/update-protocol.md`.

Do not delete raw issues. They are audit history.
