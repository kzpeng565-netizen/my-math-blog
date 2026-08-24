---
name: obsidian-vault-notes
description: Safely retrieve and read notes in this Obsidian vault without admitting MathInk stroke payloads into model context.
---

# Safe Vault Note Reading

Prefer the sanitized local recall wrapper:

```powershell
python "C:\Users\15345\.codex\skills\obsidian-vault-notes\scripts\recall_notes.py" --status-only --vault-root "D:\mathblog\quartz\content"
python "C:\Users\15345\.codex\skills\obsidian-vault-notes\scripts\recall_notes.py" --query "topic" --vault-root "D:\mathblog\quartz\content"
python "C:\Users\15345\.codex\skills\obsidian-vault-notes\scripts\recall_notes.py" --note "Note title" --vault-root "D:\mathblog\quartz\content"
```

The wrapper and index parser replace MathInk `%%inkedmark` and fenced `inkedmark` stroke payloads with a `手写笔记` placeholder while preserving inline caption/recognized text.

Never emit or inspect raw `v<n>:<base64>` stroke data. Do not use a raw whole-file read for a mixed handwriting note. Query metadata first and expand only the content authorized by the user. Rebuild a stale index before relying on broad retrieval.
