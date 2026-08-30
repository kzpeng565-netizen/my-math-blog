from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from common import parse_timestamp


TAG_STRENGTHS = {"fact", "hard", "strong", "hint"}
ACTIVITIES = {
    "work",
    "entertainment",
    "shopping",
    "brief_communication",
    "rest",
    "other",
    "uncertain",
}
OPERATORS = {
    "equals",
    "contains",
    "regex",
    "in",
    "exists",
    "gte",
    "lte",
}


def load_tag_rules(path: Path) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    errors = validate_tag_rules(config)
    if errors:
        raise ValueError("tag规则配置无效：" + "；".join(errors))
    canonical = json.dumps(
        config, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return {
        **config,
        "_rule_version": "sha256:" + hashlib.sha256(canonical).hexdigest(),
    }


def validate_tag_rules(config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if config.get("schema_version") != 1:
        errors.append("schema_version必须为1")
    definitions = config.get("tag_definitions")
    if not isinstance(definitions, dict):
        errors.append("tag_definitions必须是对象")
        definitions = {}
    rules = config.get("rules")
    if not isinstance(rules, list):
        return [*errors, "rules必须是数组"]

    seen_ids: set[str] = set()
    for index, rule in enumerate(rules):
        prefix = f"rules[{index}]"
        if not isinstance(rule, dict):
            errors.append(f"{prefix}必须是对象")
            continue
        rule_id = rule.get("id")
        if not isinstance(rule_id, str) or not rule_id.strip():
            errors.append(f"{prefix}.id不能为空")
        elif rule_id in seen_ids:
            errors.append(f"{prefix}.id重复：{rule_id}")
        else:
            seen_ids.add(rule_id)
        if not isinstance(rule.get("enabled", True), bool):
            errors.append(f"{prefix}.enabled必须是布尔值")
        try:
            int(rule.get("priority", 0))
        except (TypeError, ValueError):
            errors.append(f"{prefix}.priority必须是整数")
        errors.extend(_validate_match(rule.get("match"), f"{prefix}.match"))
        additions = rule.get("add_tags", [])
        if not isinstance(additions, list):
            errors.append(f"{prefix}.add_tags必须是数组")
        else:
            for tag_index, tag in enumerate(additions):
                tag_prefix = f"{prefix}.add_tags[{tag_index}]"
                if not isinstance(tag, dict):
                    errors.append(f"{tag_prefix}必须是对象")
                    continue
                name = tag.get("name")
                if name not in definitions:
                    errors.append(f"{tag_prefix}.name未在tag_definitions中定义")
                if tag.get("strength") not in TAG_STRENGTHS:
                    errors.append(f"{tag_prefix}.strength不在允许列表中")
        removals = rule.get("remove_tags", [])
        if not isinstance(removals, list) or not all(
            isinstance(name, str) and name in definitions for name in removals
        ):
            errors.append(f"{prefix}.remove_tags必须只包含已定义tag名称")
        locked = rule.get("locked_activity")
        if locked is not None and locked not in ACTIVITIES:
            errors.append(f"{prefix}.locked_activity不在允许列表中")
        if not isinstance(rule.get("force_boundary", False), bool):
            errors.append(f"{prefix}.force_boundary必须是布尔值")
    return errors


def _validate_match(node: Any, path: str) -> list[str]:
    if not isinstance(node, dict):
        return [f"{path}必须是对象"]
    compound_keys = [key for key in ("all", "any", "not") if key in node]
    if compound_keys:
        if len(compound_keys) != 1:
            return [f"{path}只能使用一个组合操作符"]
        key = compound_keys[0]
        value = node[key]
        if key == "not":
            return _validate_match(value, f"{path}.not")
        if not isinstance(value, list) or not value:
            return [f"{path}.{key}必须是非空数组"]
        errors: list[str] = []
        for index, child in enumerate(value):
            errors.extend(_validate_match(child, f"{path}.{key}[{index}]"))
        return errors
    if not isinstance(node.get("field"), str):
        return [f"{path}.field必须是字符串"]
    operator = node.get("operator")
    if operator not in OPERATORS:
        return [f"{path}.operator不在允许列表中"]
    if operator != "exists" and "value" not in node:
        return [f"{path}.value不能为空"]
    if operator == "regex":
        try:
            re.compile(str(node.get("value", "")))
        except re.error as error:
            return [f"{path}.value不是有效正则：{error}"]
    return []


def _get_field(item: dict[str, Any], field: str) -> Any:
    current: Any = item
    for part in field.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _text(value: Any, ignore_case: bool) -> str:
    result = "" if value is None else str(value)
    return result.casefold() if ignore_case else result


def _matches(node: dict[str, Any], item: dict[str, Any]) -> bool:
    if "all" in node:
        return all(_matches(child, item) for child in node["all"])
    if "any" in node:
        return any(_matches(child, item) for child in node["any"])
    if "not" in node:
        return not _matches(node["not"], item)

    actual = _get_field(item, node["field"])
    operator = node["operator"]
    expected = node.get("value")
    ignore_case = bool(node.get("ignore_case", True))
    if operator == "exists":
        return (actual is not None and actual != "") == bool(expected)
    if operator == "equals":
        return _text(actual, ignore_case) == _text(expected, ignore_case)
    if operator == "contains":
        return _text(expected, ignore_case) in _text(actual, ignore_case)
    if operator == "regex":
        flags = re.IGNORECASE if ignore_case else 0
        return re.search(str(expected), _text(actual, False), flags) is not None
    if operator == "in":
        if not isinstance(expected, list):
            return False
        return _text(actual, ignore_case) in {
            _text(value, ignore_case) for value in expected
        }
    try:
        number = float(actual)
        threshold = float(expected)
    except (TypeError, ValueError):
        return False
    if operator == "gte":
        return number >= threshold
    if operator == "lte":
        return number <= threshold
    return False


def _prepared_timeline(
    items: list[dict[str, Any]], timezone_name: str
) -> list[tuple[datetime, datetime, dict[str, Any]]]:
    prepared: list[tuple[datetime, datetime, dict[str, Any]]] = []
    for item in items:
        try:
            start = parse_timestamp(item["start"], timezone_name)
            end = parse_timestamp(item["end"], timezone_name)
        except (KeyError, TypeError, ValueError):
            continue
        if end > start:
            prepared.append((start, end, item))
    return prepared


def _covering(
    items: list[tuple[datetime, datetime, dict[str, Any]]],
    start: datetime,
    end: datetime,
) -> dict[str, Any] | None:
    return next(
        (item for left, right, item in items if left <= start and right >= end),
        None,
    )


def _device_fact(
    status_item: dict[str, Any] | None,
    activity_item: dict[str, Any] | None,
    *,
    mobile: bool = False,
) -> dict[str, Any]:
    if mobile:
        result = {
            "screen": status_item.get("state", "unknown")
            if status_item
            else "unknown"
        }
        if activity_item:
            result.update(
                {
                    "app": activity_item.get("app_display", ""),
                    "package": activity_item.get("package", ""),
                }
            )
        return {key: value for key, value in result.items() if value != ""}

    result = {
        "status": status_item.get("status", "unknown")
        if status_item
        else "unknown"
    }
    if activity_item:
        result.update(
            {
                "app": activity_item.get("app_display", ""),
                "process": activity_item.get("app", ""),
                "title": activity_item.get("title", ""),
                "domain": activity_item.get("domain", ""),
            }
        )
    return {key: value for key, value in result.items() if value != ""}


def _overlap_seconds(
    left: datetime, right: datetime, start: datetime, end: datetime
) -> float:
    return max(0.0, (min(right, end) - max(left, start)).total_seconds())


def _mobile_summary(
    status_items: list[tuple[datetime, datetime, dict[str, Any]]],
    activity_items: list[tuple[datetime, datetime, dict[str, Any]]],
    start: datetime,
    end: datetime,
) -> dict[str, Any]:
    screen_seconds: Counter[str] = Counter()
    for left, right, item in status_items:
        seconds = _overlap_seconds(left, right, start, end)
        if seconds:
            screen_seconds[str(item.get("state", "unknown"))] += seconds
    screen = (
        screen_seconds.most_common(1)[0][0] if screen_seconds else "unknown"
    )
    result: dict[str, Any] = {"screen": screen}
    if screen_seconds.get("on", 0):
        result["screen_on_seconds"] = round(screen_seconds["on"], 3)

    app_seconds: Counter[tuple[str, str]] = Counter()
    for left, right, item in activity_items:
        seconds = _overlap_seconds(left, right, start, end)
        if seconds:
            key = (
                str(item.get("app_display", "")),
                str(item.get("package", "")),
            )
            app_seconds[key] += seconds
    if app_seconds:
        ordered = app_seconds.most_common(4)
        result["app"] = ordered[0][0][0]
        if ordered[0][0][1]:
            result["package"] = ordered[0][0][1]
        result["apps"] = [
            {
                "app": key[0],
                "seconds": round(seconds, 1),
            }
            for key, seconds in ordered
            if key[0]
        ]
        result["apps_text"] = "|".join(
            key[0] for key, _ in ordered if key[0]
        )
    return result


def _in_interval(
    start: datetime,
    end: datetime,
    intervals: list[tuple[datetime, datetime]],
) -> bool:
    return any(left <= start and right >= end for left, right in intervals)


def _apply_rules(
    block: dict[str, Any], rules_config: dict[str, Any]
) -> dict[str, Any]:
    tags: list[dict[str, str]] = list(block.get("tags", []))
    trace: list[dict[str, str]] = list(block.get("tag_trace", []))
    locked_activities: list[tuple[int, str, str]] = []
    if block.get("locked_activity"):
        locked_activities.append(
            (
                10_000,
                str(block["locked_activity"]),
                str(block.get("lock_rule_id", "core")),
            )
        )
    force_boundary = bool(block.get("force_boundary"))
    rules = sorted(
        (
            rule
            for rule in rules_config["rules"]
            if rule.get("enabled", True)
        ),
        key=lambda rule: (int(rule.get("priority", 0)), rule["id"]),
    )
    for rule in rules:
        if not _matches(rule["match"], block):
            continue
        removed = set(rule.get("remove_tags", []))
        if removed:
            tags = [tag for tag in tags if tag["name"] not in removed]
            trace = [item for item in trace if item["tag"] not in removed]
        for tag in rule.get("add_tags", []):
            item = {"name": tag["name"], "strength": tag["strength"]}
            if item not in tags:
                tags.append(item)
            trace.append({"tag": tag["name"], "rule_id": rule["id"]})
        if rule.get("locked_activity"):
            locked_activities.append(
                (
                    int(rule.get("priority", 0)),
                    rule["locked_activity"],
                    rule["id"],
                )
            )
        force_boundary = force_boundary or bool(rule.get("force_boundary"))

    if locked_activities:
        top_priority = max(item[0] for item in locked_activities)
        strongest = [
            item for item in locked_activities if item[0] == top_priority
        ]
        activities = {item[1] for item in strongest}
        if len(activities) == 1:
            block["locked_activity"] = strongest[0][1]
            block["lock_rule_id"] = strongest[0][2]
        else:
            tags.append({"name": "rule_conflict", "strength": "hard"})
            trace.extend(
                {"tag": "rule_conflict", "rule_id": item[2]}
                for item in strongest
            )
    if tags:
        block["tags"] = tags
        block["tag_trace"] = trace
    if force_boundary:
        block["force_boundary"] = True
    return block


def _merge_blocks(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    ignored = {"id", "start", "end", "duration_seconds"}
    for block in blocks:
        if merged:
            previous = merged[-1]
            previous_signature = {
                key: value for key, value in previous.items() if key not in ignored
            }
            current_signature = {
                key: value for key, value in block.items() if key not in ignored
            }
            if previous["end"] == block["start"] and previous_signature == current_signature:
                previous["end"] = block["end"]
                previous["duration_seconds"] = round(
                    float(previous["duration_seconds"])
                    + float(block["duration_seconds"]),
                    3,
                )
                continue
        merged.append(dict(block))
    for index, block in enumerate(merged, start=1):
        prefix = "r" if block["scope"] == "report" else "c"
        block["id"] = f"{prefix}{index:03d}"
    return merged


def build_tagged_fact_view(
    settings: dict[str, Any],
    rules_path: Path,
    report_start: datetime,
    report_end: datetime,
    computer_facts: dict[str, Any],
    phone_facts: dict[str, Any],
    tablet_facts: dict[str, Any],
    cross_device_facts: dict[str, Any],
) -> dict[str, Any]:
    timezone_name = settings["timezone"]
    rules_config = load_tag_rules(rules_path)
    context_start = parse_timestamp(
        computer_facts["period"]["start"], timezone_name
    )
    context_end = parse_timestamp(computer_facts["period"]["end"], timezone_name)
    timelines = {
        "computer_status": _prepared_timeline(
            computer_facts.get("status_timeline", []), timezone_name
        ),
        "computer_activity": _prepared_timeline(
            computer_facts.get("timeline", []), timezone_name
        ),
        "phone_screen": _prepared_timeline(
            phone_facts.get("screen_timeline", []), timezone_name
        ),
        "phone_activity": _prepared_timeline(
            phone_facts.get("timeline", []), timezone_name
        ),
        "tablet_screen": _prepared_timeline(
            tablet_facts.get("screen_timeline", []), timezone_name
        ),
        "tablet_activity": _prepared_timeline(
            tablet_facts.get("timeline", []), timezone_name
        ),
    }
    confirmed_rest = [
        (
            parse_timestamp(item["start"], timezone_name),
            parse_timestamp(item["end"], timezone_name),
        )
        for item in cross_device_facts.get("rest_rule", {}).get(
            "confirmed_rest_intervals", []
        )
    ]

    boundaries = {context_start, report_start, report_end, context_end}
    for key in ("computer_status", "computer_activity"):
        timeline = timelines[key]
        for start, end, _ in timeline:
            if end > context_start and start < context_end:
                boundaries.add(max(start, context_start))
                boundaries.add(min(end, context_end))
    for start, end in confirmed_rest:
        boundaries.add(max(start, context_start))
        boundaries.add(min(end, context_end))

    primary_boundaries = sorted(boundaries)
    mobile_boundaries: set[datetime] = set()
    for start, end in zip(primary_boundaries, primary_boundaries[1:]):
        computer_status = _covering(
            timelines["computer_status"], start, end
        )
        computer_active = (
            computer_status is not None
            and computer_status.get("status") == "not-afk"
        )
        if computer_active or _in_interval(start, end, confirmed_rest):
            continue
        for key in (
            "phone_screen",
            "phone_activity",
            "tablet_screen",
            "tablet_activity",
        ):
            for left, right, _ in timelines[key]:
                if right > start and left < end:
                    mobile_boundaries.add(max(left, start))
                    mobile_boundaries.add(min(right, end))
    boundaries.update(mobile_boundaries)

    ordered = sorted(boundaries)
    blocks: list[dict[str, Any]] = []
    for start, end in zip(ordered, ordered[1:]):
        if end <= start:
            continue
        if end <= report_start:
            scope = "context_before"
        elif start >= report_end:
            scope = "context_after"
        else:
            scope = "report"
        block = {
            "id": "",
            "scope": scope,
            "start": start.isoformat(timespec="seconds"),
            "end": end.isoformat(timespec="seconds"),
            "duration_seconds": round((end - start).total_seconds(), 3),
            "computer": _device_fact(
                _covering(timelines["computer_status"], start, end),
                _covering(timelines["computer_activity"], start, end),
            ),
            "phone": _mobile_summary(
                timelines["phone_screen"],
                timelines["phone_activity"],
                start,
                end,
            ),
            "tablet": _mobile_summary(
                timelines["tablet_screen"],
                timelines["tablet_activity"],
                start,
                end,
            ),
        }
        if scope == "report" and _in_interval(start, end, confirmed_rest):
            block["tags"] = [{"name": "confirmed_rest", "strength": "hard"}]
            block["tag_trace"] = [
                {"tag": "confirmed_rest", "rule_id": "core.confirmed_rest"}
            ]
            block["locked_activity"] = "rest"
            block["lock_rule_id"] = "core.confirmed_rest"
            block["force_boundary"] = True
        block = _apply_rules(block, rules_config)
        blocks.append(block)

    blocks = _merge_blocks(blocks)
    used_tags = {
        tag["name"]
        for block in blocks
        for tag in block.get("tags", [])
    }
    return {
        "schema_version": 1,
        "source": "deterministic_tagged_fact_blocks",
        "tag_rule_version": rules_config["_rule_version"],
        "context_period": {
            "start": context_start.isoformat(timespec="seconds"),
            "end": context_end.isoformat(timespec="seconds"),
        },
        "report_period": {
            "start": report_start.isoformat(timespec="seconds"),
            "end": report_end.isoformat(timespec="seconds"),
        },
        "noise_gap_seconds": float(
            settings.get("processing", {}).get(
                "timeline_noise_gap_seconds", 3
            )
        ),
        "tag_definitions": {
            name: rules_config["tag_definitions"][name]
            for name in sorted(used_tags)
            if name in rules_config["tag_definitions"]
        },
        "blocks": blocks,
        "quality": {
            "computer": computer_facts.get("quality", {}),
            "phone": phone_facts.get("quality", {}),
            "tablet": tablet_facts.get("quality", {}),
        },
    }


def compact_fact_view_for_ai(view: dict[str, Any]) -> dict[str, Any]:
    def compact_block(
        block: dict[str, Any], *, include_id: bool
    ) -> dict[str, Any]:
        computer = block.get("computer", {})
        phone = block.get("phone", {})
        tablet = block.get("tablet", {})
        computer_values = [
            computer.get("status", "unknown"),
            computer.get("app", ""),
            computer.get("title", ""),
            computer.get("domain", ""),
        ]
        while len(computer_values) > 1 and computer_values[-1] == "":
            computer_values.pop()

        def compact_mobile(device: dict[str, Any]) -> Any:
            apps = [
                [item["app"], item["seconds"]]
                for item in device.get("apps", [])[:3]
            ]
            screen = device.get("screen", "unknown")
            return [screen, apps] if apps else screen

        compact: dict[str, Any] = {
            "time": str(block["start"])[11:19],
            "seconds": block["duration_seconds"],
            "c": computer_values,
            "p": compact_mobile(phone),
            "t": compact_mobile(tablet),
        }
        if include_id:
            compact["id"] = block["id"]
        if block.get("tags"):
            compact["tags"] = [
                f"{tag['name']}:{tag['strength']}"
                for tag in block["tags"]
            ]
        if block.get("locked_activity"):
            compact["locked"] = block["locked_activity"]
        if block.get("force_boundary") and not block.get("locked_activity"):
            compact["boundary"] = True
        return compact

    context_blocks: list[dict[str, Any]] = []
    report_candidates: list[dict[str, Any]] = []
    locked_markers: list[dict[str, Any]] = []
    candidate_map: dict[str, list[str]] = {}
    noise_gap_seconds = float(view.get("noise_gap_seconds", 3))
    pending_short: list[dict[str, Any]] = []
    candidate_blocks: list[dict[str, Any]] = []
    zone = 1

    def append_candidate(source_blocks: list[dict[str, Any]]) -> None:
        if not source_blocks:
            return
        anchor = max(
            source_blocks,
            key=lambda item: float(item["duration_seconds"]),
        )
        compact = compact_block(anchor, include_id=False)
        alias = f"u{len(report_candidates) + 1:03d}"
        compact["id"] = alias
        compact["zone"] = zone
        compact["time"] = str(source_blocks[0]["start"])[11:19]
        compact["seconds"] = round(
            sum(float(item["duration_seconds"]) for item in source_blocks),
            3,
        )
        all_tags = list(
            dict.fromkeys(
                f"{tag['name']}:{tag['strength']}"
                for item in source_blocks
                for tag in item.get("tags", [])
            )
        )
        if all_tags:
            compact["tags"] = all_tags
        if any(item.get("force_boundary") for item in source_blocks):
            compact["boundary"] = True
        report_candidates.append(compact)
        candidate_map[alias] = [item["id"] for item in source_blocks]

    def flush_candidate() -> None:
        nonlocal candidate_blocks, pending_short
        if candidate_blocks:
            append_candidate(candidate_blocks)
        elif pending_short:
            append_candidate(pending_short)
        candidate_blocks = []
        pending_short = []

    for block in view.get("blocks", []):
        if block.get("scope") != "report":
            compact = compact_block(block, include_id=False)
            compact["scope"] = block["scope"]
            context_blocks.append(compact)
        elif block.get("locked_activity"):
            flush_candidate()
            marker = compact_block(block, include_id=False)
            marker["zone_before"] = zone
            zone += 1
            marker["zone_after"] = zone
            locked_markers.append(marker)
        elif block.get("force_boundary"):
            flush_candidate()
            zone += 1
            append_candidate([block])
            zone += 1
        else:
            is_short = (
                float(block.get("duration_seconds", 0))
                <= noise_gap_seconds
            )
            if is_short:
                if candidate_blocks:
                    candidate_blocks.append(block)
                else:
                    pending_short.append(block)
            else:
                if candidate_blocks:
                    flush_candidate()
                candidate_blocks = [*pending_short, block]
                pending_short = []
    flush_candidate()

    return {
        "schema_version": view["schema_version"],
        "tag_rule_version": view["tag_rule_version"],
        "context_period": view["context_period"],
        "report_period": view["report_period"],
        "block_schema": {
            "c": ["computer_status", "app", "title", "domain"],
            "p": "screen_state or [screen_state, [[app, overlap_seconds]]]",
            "t": "screen_state or [screen_state, [[app, overlap_seconds]]]",
            "tags": ["tag_name:strength"],
            "boundary": "candidate must be grouped alone",
            "zone": "groups may contain candidates from one zone only",
        },
        "tag_definitions": view.get("tag_definitions", {}),
        "context_blocks": context_blocks,
        "locked_markers": locked_markers,
        "report_candidates": report_candidates,
        "_candidate_map": candidate_map,
        "quality": {
            device: {
                "level": quality.get("level", "low"),
                "material_issues": quality.get("material_issues", []),
            }
            for device, quality in view.get("quality", {}).items()
        },
    }


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Validate or explain tag rules")
    parser.add_argument(
        "--rules",
        default=str(project_root / "config" / "tag_rules.json"),
    )
    parser.add_argument(
        "--explain-block",
        help="Path to one JSON fact block to evaluate against the rules",
    )
    arguments = parser.parse_args()
    try:
        rules = load_tag_rules(Path(arguments.rules))
        result: dict[str, Any] = {
            "status": "valid",
            "rule_version": rules["_rule_version"],
            "enabled_rules": sum(
                bool(rule.get("enabled", True)) for rule in rules["rules"]
            ),
        }
        if arguments.explain_block:
            block = json.loads(
                Path(arguments.explain_block).read_text(encoding="utf-8")
            )
            if not isinstance(block, dict):
                raise ValueError("事实块JSON必须是对象")
            result["matched_result"] = _apply_rules(dict(block), rules)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(
            json.dumps(
                {
                    "status": "invalid",
                    "error": f"{type(error).__name__}: {error}",
                },
                ensure_ascii=False,
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
