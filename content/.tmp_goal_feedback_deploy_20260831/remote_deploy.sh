#!/usr/bin/env bash
set -euo pipefail

garden="/home/conrad/services/focus-garden"
advisor="/home/conrad/workspace/activitywatch-advisor"
incoming="/tmp/goal-feedback-v2-incoming"
backup="$(cat /tmp/goal-feedback-v2-backup-path)"

rollback() {
  cp -a "${backup}/garden/static/index.html" "${garden}/static/index.html"
  cp -a "${backup}/garden/static/app.js" "${garden}/static/app.js"
  cp -a "${backup}/garden/static/style.css" "${garden}/static/style.css"
  cp -a "${backup}/garden/tests/test_service.py" "${garden}/tests/test_service.py"
  cp -a "${backup}/advisor/src/goal_agent.py" "${advisor}/src/goal_agent.py"
  cp -a "${backup}/advisor/tests/test_goal_agent.py" "${advisor}/tests/test_goal_agent.py"
  sudo systemctl restart activitywatch-advisor-web.service focus-garden.service || true
}

trap 'code=$?; if [ "$code" -ne 0 ]; then rollback; fi; exit "$code"' EXIT

install -m 0644 "${incoming}/index.html" "${garden}/static/index.html"
install -m 0644 "${incoming}/app.js" "${garden}/static/app.js"
install -m 0644 "${incoming}/style.css" "${garden}/static/style.css"
install -m 0644 "${incoming}/test_service.py" "${garden}/tests/test_service.py"
install -m 0644 "${incoming}/goal_agent.py" "${advisor}/src/goal_agent.py"
install -m 0644 "${incoming}/test_goal_agent.py" "${advisor}/tests/test_goal_agent.py"

python3 -m py_compile "${advisor}/src/goal_agent.py" "${advisor}/tests/test_goal_agent.py" "${garden}/tests/test_service.py"
node -e 'const fs=require("fs"); new Function(fs.readFileSync(process.argv[1],"utf8")); console.log("browser-script-parse-ok")' "${garden}/static/app.js"

cd "${advisor}"
python3 -m unittest \
  tests.test_goal_agent.GoalAgentTest.test_v2_exercise_keeps_performance_conditions_and_boundary \
  tests.test_goal_agent.GoalAgentTest.test_v2_exercise_rejects_impossible_counts \
  tests.test_goal_agent.GoalAgentTest.test_v2_grade_preserves_confirmed_weight \
  tests.test_goal_agent.GoalAgentCalculationsTest.test_v2_mock_requires_new_timed_independent_verified_conditions \
  tests.test_goal_agent.GoalAgentCalculationsTest.test_v2_self_estimated_grade_is_not_used_in_scenario

cd "${garden}"
python3 -m unittest tests.test_service.GardenServiceTests.test_goal_mode_exposes_course_progress_and_gpt_sol_without_deepseek_fallback

sudo systemctl restart activitywatch-advisor-web.service focus-garden.service
sudo systemctl is-active --quiet activitywatch-advisor-web.service
sudo systemctl is-active --quiet focus-garden.service

trap - EXIT
printf 'deployed-backup=%s\n' "${backup}"
