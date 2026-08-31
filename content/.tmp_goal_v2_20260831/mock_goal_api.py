from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


COURSE_UNITS = [
    {
        "id": "differential-geometry-01-01",
        "chapter_no": 1,
        "chapter_title": "平面曲线与空间曲线",
        "section_no": 1,
        "title": "平面曲线",
        "sort_order": 1,
        "mastery": 0,
    },
    {
        "id": "differential-geometry-01-02",
        "chapter_no": 1,
        "chapter_title": "平面曲线与空间曲线",
        "section_no": 2,
        "title": "平面曲线例子",
        "sort_order": 2,
        "mastery": 0,
    },
    {
        "id": "differential-geometry-01-03",
        "chapter_no": 1,
        "chapter_title": "平面曲线与空间曲线",
        "section_no": 3,
        "title": "平面曲线基本定理",
        "sort_order": 3,
        "mastery": 0,
    },
]


STATE = {
    "schema_version": 2,
    "plan_version": 2,
    "generated_at": "2026-08-31T13:56:00+08:00",
    "portfolio": {
        "title": "2028 级保研到数学所何伟鲲方向",
        "institution": "中国科学院数学与系统科学研究院",
        "direction": "何伟鲲方向",
        "target_date": "2027-09-30",
        "trial_ends_on": "2026-09-27",
        "capacity_min_minutes": 1320,
        "capacity_max_minutes": 1860,
    },
    "tracks": [
        {
            "id": "track-courses",
            "code": "courses",
            "title": "专业课三门均 ≥90",
            "weight": 0.4,
            "outcome_definition": "概率论、泛函分析、微分几何课程总评均不低于 90。",
            "status": "unknown",
            "content_coverage": {"ratio": None},
            "weekly_execution": {"rate": None},
            "throughput_forecast": {"status": "unknown", "weekly_minutes": None},
            "evidence_confidence": "unknown",
            "evidence_count": 0,
            "course_scenarios": {
                name: {
                    "profile_status": "partial_confirmed",
                    "required_remaining_average": None,
                    "progress": {
                        "confirmed_taught_units": 0,
                        "total_units": 36 if name == "微分几何" else 40,
                    },
                }
                for name in ("概率论", "泛函分析", "微分几何")
            },
        },
        {
            "id": "track-amss-exam",
            "code": "amss_exam",
            "title": "数学所笔试",
            "weight": 0.2,
            "outcome_definition": "不同真实题源连续三次限时 ≥120/150。",
            "status": "unknown",
            "content_coverage": {"ratio": None},
            "weekly_execution": {"rate": None},
            "throughput_forecast": {"status": "unknown"},
            "evidence_confidence": "unknown",
            "evidence_count": 0,
            "mastery": {},
        },
    ],
    "throughput": {
        "status": "unknown",
        "forecast_weekly_minutes": None,
        "reason": "少于三周可比深度学习数据。",
    },
    "execution": {"status": "unknown", "rate": None},
    "current_week": {
        "week_start": "2026-08-31",
        "deep_minutes": 1590,
        "items": [
            {
                "id": "w1-c-d1",
                "track_id": "track-courses",
                "track_title": "专业课三门均 ≥90",
                "course_id": "differential-geometry",
                "title": "微分几何：按实际授课小节建立掌握闭环",
                "description": "先由用户确认本周实际讲到的小节；只使用 MathInk 可见层。",
                "deep_minutes": 120,
                "recommended_date": "2026-09-01",
                "accepted_date": None,
                "status": "planned",
                "input_state": "awaiting_course_progress",
                "material_status": "ready",
                "material_required": 1,
                "task_id": None,
                "sync_status": None,
            },
            {
                "id": "w1-e-1",
                "track_id": "track-amss-exam",
                "track_title": "数学所笔试",
                "course_id": None,
                "title": "数学所笔试：真实题源与考查范围待核验",
                "description": "资料不足时不生成虚假基线。",
                "deep_minutes": 180,
                "recommended_date": "2026-09-05",
                "accepted_date": None,
                "status": "planned",
                "input_state": "awaiting_material",
                "material_status": "pending",
                "material_required": 1,
                "task_id": None,
                "sync_status": None,
            },
        ],
    },
    "course_profiles": [
        {
            "id": "probability",
            "name": "概率论",
            "course_code": "B0111005H",
            "teacher": "施展",
            "textbooks": ["Ross《概率论基础教程》"],
            "assessment_weights": {
                "midterm": 0.3,
                "homework": 0.15,
                "thinking_problems": 0.15,
                "final": 0.4,
            },
            "exam_date": None,
            "confirmation_status": "partial_confirmed",
            "hours_warning": "64 学时与详细表 120 学时冲突。",
        },
        {
            "id": "functional-analysis",
            "name": "泛函分析",
            "course_code": "B0111011H",
            "teacher": "韩丕功",
            "textbooks": ["Brezis《泛函分析》"],
            "assessment_weights": {
                "midterm": 0.3,
                "final": 0.5,
                "coursework": 0.2,
            },
            "exam_date": None,
            "confirmation_status": "partial_confirmed",
            "hours_warning": "64 学时与详细表 76 学时冲突。",
        },
        {
            "id": "differential-geometry",
            "name": "微分几何",
            "course_code": "B0111006H",
            "teacher": "王晋民",
            "textbooks": ["Tapp, Differential Geometry of Curves and Surfaces"],
            "assessment_weights": {
                "midterm": 0.3,
                "final": 0.4,
                "coursework": 0.3,
            },
            "exam_date": None,
            "confirmation_status": "partial_confirmed",
            "hours_warning": "64 学时与章节合计 74 学时冲突。",
        },
    ],
    "course_progress": {
        "scale": {
            "0": "未接触",
            "1": "听过或能看材料",
            "2": "能复述定义/定理",
            "3": "能独立证明或解题",
        },
        "pending_input": ["概率论", "泛函分析", "微分几何"],
        "by_course": {
            "概率论": {
                "course_id": "probability",
                "units": [],
                "total_units": 46,
                "confirmed_taught_units": 0,
                "mastery_distribution": {"0": 0, "1": 0, "2": 0, "3": 0},
                "latest": None,
            },
            "泛函分析": {
                "course_id": "functional-analysis",
                "units": [],
                "total_units": 29,
                "confirmed_taught_units": 0,
                "mastery_distribution": {"0": 0, "1": 0, "2": 0, "3": 0},
                "latest": None,
            },
            "微分几何": {
                "course_id": "differential-geometry",
                "units": COURSE_UNITS,
                "total_units": 36,
                "confirmed_taught_units": 0,
                "mastery_distribution": {"0": 0, "1": 0, "2": 0, "3": 0},
                "latest": None,
            },
        },
    },
    "materials": {
        "manifest_path": "非笔记内容/任务计划/目标模式资料清单.md",
        "gaps": ["三门课考试日期待通知", "数学所真实题源待补充"],
        "documents": [
            {
                "title": "微分几何学习目录 · 几何/微分几何/1.1.md",
                "page_count": 1,
                "status": "indexed",
                "metadata": {"note_format": "mathink_markdown"},
            }
        ],
    },
    "sources": [],
    "approvals": [],
    "chat_messages": [],
    "model": {
        "name": "gpt-5.6-sol",
        "protocol": "responses",
        "reasoning_effort": "medium",
        "configured": True,
        "fallback_provider": None,
    },
    "boundaries": {
        "automatic": ["同月周任务", "推荐日", "任务拆分"],
        "approval_required": ["总目标", "截止日期", "资源权重"],
    },
}

PLAN = {
    "plan_version": 2,
    "milestones": [
        {
            "period_start": "2026-08-31",
            "period_end": "2026-09-27",
            "title": "4 周灰度试运行",
            "acceptance": ["按实际授课进度建档", "4 次可回退复盘"],
        }
    ],
    "versions": [
        {
            "id": 2,
            "created_at": "2026-08-31T13:50:00+08:00",
            "reason": "课程计划改为实际授课进度闭环",
            "actor": "system",
            "trigger": "schema_v2_migration",
            "changes": [{"field": "course_progress_mode"}],
            "rollback_of": None,
        }
    ],
}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/api/goal-agent/state":
            return self.respond(STATE)
        if self.path == "/api/goal-agent/plan":
            return self.respond(PLAN)
        if self.path.startswith("/api/task-sync/"):
            return self.respond({"revision": 0, "tasks": {}, "completed_today": []})
        if self.path.startswith("/api/recent-context"):
            return self.respond({"revision": 0, "items": []})
        self.send_error(404)

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        if length:
            self.rfile.read(length)
        self.respond({"ok": True, "plan_version": 2})

    def respond(self, value: object) -> None:
        data = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args: object) -> None:
        return


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8767), Handler).serve_forever()
