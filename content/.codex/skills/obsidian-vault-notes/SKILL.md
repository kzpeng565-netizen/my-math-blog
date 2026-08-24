---
name: obsidian-vault-notes
description: Safely retrieve and read notes in this Obsidian vault without admitting MathInk stroke payloads into model context.
---

# Safe Vault Note Reading

Use the installed local wrapper instead of a raw whole-file read:

```powershell
python "C:\Users\15345\.codex\skills\obsidian-vault-notes\scripts\recall_notes.py" --status-only --vault-root "D:\mathblog\quartz\content"
python "C:\Users\15345\.codex\skills\obsidian-vault-notes\scripts\recall_notes.py" --query "topic" --vault-root "D:\mathblog\quartz\content"
python "C:\Users\15345\.codex\skills\obsidian-vault-notes\scripts\recall_notes.py" --note "Note title" --vault-root "D:\mathblog\quartz\content"
```

The wrapper and index parser replace MathInk `%%inkedmark` and fenced `inkedmark` payloads with a `手写笔记` placeholder. Inline caption/recognized text is preserved.

Never emit or inspect raw `v<n>:<base64>` stroke data. Do not use `Get-Content`, `rg` context output, or generic whole-file reads on a mixed handwriting note. Use metadata-only query first; expand note content only within the user's authorized scope.

If `index_status.index_stale` is true, rebuild with the installed skill's `scripts\rebuild_index.ps1`, then retry. An index miss is not proof that no note exists.
