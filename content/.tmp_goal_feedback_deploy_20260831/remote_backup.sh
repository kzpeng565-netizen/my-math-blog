#!/usr/bin/env bash
set -euo pipefail

stamp="$(date +%Y%m%d-%H%M%S)"
backup="/home/conrad/workspace/backups/goal-feedback-v2-${stamp}"
garden="/home/conrad/services/focus-garden"
advisor="/home/conrad/workspace/activitywatch-advisor"
database="${advisor}/data/goal_agent/goal-agent.sqlite3"

mkdir -p "${backup}/garden/static" "${backup}/garden/tests" "${backup}/advisor/src" "${backup}/advisor/tests" "${backup}/database"
cp -a "${garden}/static/index.html" "${backup}/garden/static/index.html"
cp -a "${garden}/static/app.js" "${backup}/garden/static/app.js"
cp -a "${garden}/static/style.css" "${backup}/garden/static/style.css"
cp -a "${garden}/tests/test_service.py" "${backup}/garden/tests/test_service.py"
cp -a "${advisor}/src/goal_agent.py" "${backup}/advisor/src/goal_agent.py"
cp -a "${advisor}/tests/test_goal_agent.py" "${backup}/advisor/tests/test_goal_agent.py"

python3 -c 'import sqlite3,sys; source=sqlite3.connect(sys.argv[1]); target=sqlite3.connect(sys.argv[2]); source.backup(target); target.close(); source.close()' "${database}" "${backup}/database/goal-agent.sqlite3"
chmod 600 "${backup}/database/goal-agent.sqlite3"
python3 -c 'import sqlite3,sys; db=sqlite3.connect(sys.argv[1]); result=db.execute("PRAGMA quick_check").fetchone()[0]; db.close(); print("database-quick-check=" + result); raise SystemExit(0 if result == "ok" else 1)' "${backup}/database/goal-agent.sqlite3"

sha256sum \
  "${backup}/garden/static/index.html" \
  "${backup}/garden/static/app.js" \
  "${backup}/garden/static/style.css" \
  "${backup}/garden/tests/test_service.py" \
  "${backup}/advisor/src/goal_agent.py" \
  "${backup}/advisor/tests/test_goal_agent.py" \
  "${backup}/database/goal-agent.sqlite3" > "${backup}/SHA256SUMS"
printf '%s\n' "${backup}" > /tmp/goal-feedback-v2-backup-path
printf 'backup=%s\n' "${backup}"
