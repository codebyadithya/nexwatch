import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "data" / "runs"


def load_json(filename: str) -> Any:
    """Load a JSON run artifact safely."""
    path = RUNS / filename

    if not path.exists():
        return None

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        return None


def extract_report(payload: Any) -> dict[str, Any] | None:
    """
    Normalize different NexWatch artifact shapes into a report.

    Some validation artifacts use:
        {"report": {...}}

    while others may contain the report directly.
    """
    if not isinstance(payload, dict):
        return None

    report = payload.get("report")

    if isinstance(report, dict):
        return report

    if "health_score" in payload or "records" in payload:
        return payload

    return None


def get_health(report: dict[str, Any] | None) -> float | None:
    if not report:
        return None

    value = report.get("health_score")

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def get_status(report: dict[str, Any] | None) -> str:
    if not report:
        return "UNKNOWN"

    return str(report.get("status", "unknown")).upper()


def get_records(
    report: dict[str, Any] | None,
) -> tuple[int, int]:
    if not report:
        return 0, 0

    records = report.get("records", {})

    if not isinstance(records, dict):
        return 0, 0

    current = records.get("current", 0)
    baseline = records.get("baseline", 0)

    try:
        current = int(current)
    except (TypeError, ValueError):
        current = 0

    try:
        baseline = int(baseline)
    except (TypeError, ValueError):
        baseline = 0

    return current, baseline


def get_deviation(
    report: dict[str, Any] | None,
) -> float:
    if not report:
        return 0.0

    records = report.get("records", {})

    if not isinstance(records, dict):
        return 0.0

    try:
        return float(records.get("deviation_percent", 0.0))
    except (TypeError, ValueError):
        return 0.0


def get_critical_issues(
    report: dict[str, Any] | None,
) -> list[str]:
    if not report:
        return []

    issues = report.get("critical_issues", [])

    if not isinstance(issues, list):
        return []

    return [str(issue) for issue in issues]


def get_warnings(
    report: dict[str, Any] | None,
) -> list[str]:
    if not report:
        return []

    warnings = report.get("warnings", [])

    if not isinstance(warnings, list):
        return []

    return [str(warning) for warning in warnings]


def extract_stories(payload: Any) -> list[dict[str, Any]]:
    """
    Extract recovered stories from repaired.json.

    Expected structure is roughly:
        [
            {
                "stories": [...]
            }
        ]
    """
    if not isinstance(payload, list):
        return []

    stories: list[dict[str, Any]] = []

    for item in payload:
        if not isinstance(item, dict):
            continue

        candidate = item.get("stories", [])

        if not isinstance(candidate, list):
            continue

        for story in candidate:
            if isinstance(story, dict):
                stories.append(story)

    return stories


def normalize_story(story: dict[str, Any]) -> dict[str, Any]:
    """Normalize one recovered story for the UI."""

    title = story.get("title") or "Untitled"

    points = story.get("points", 0)
    comments = story.get("comment_count")
    author = story.get("author") or "—"

    try:
        points = int(points)
    except (TypeError, ValueError):
        points = 0

    if comments is None or comments == "":
        comments = "—"
    else:
        try:
            comments = int(comments)
        except (TypeError, ValueError):
            comments = str(comments)

    return {
        "title": str(title),
        "points": points,
        "comments": comments,
        "author": str(author),
    }


def build_dashboard_data() -> dict[str, Any]:
    """
    Load all artifacts required by the NexWatch dashboard
    and return one normalized data object.
    """

    degraded_raw = load_json("degraded-validation.json")
    repaired_raw = load_json("final-repaired-validation.json")
    evidence = load_json("day4-recovery-evidence.json")
    repaired_data = load_json("repaired.json")

    degraded_report = extract_report(degraded_raw)
    repaired_report = extract_report(repaired_raw)

    initial_report = None

    if isinstance(evidence, dict):
        evidence_initial = evidence.get("initial_report")

        if isinstance(evidence_initial, dict):
            initial_report = evidence_initial

    if initial_report is None:
        initial_report = degraded_report

    final_report = repaired_report

    initial_health = get_health(initial_report)
    final_health = get_health(final_report)

    initial_records, baseline_records = get_records(initial_report)
    final_records, final_baseline = get_records(final_report)

    if baseline_records == 0:
        baseline_records = final_baseline

    initial_deviation = get_deviation(initial_report)
    final_deviation = get_deviation(final_report)

    improvement = None

    if initial_health is not None and final_health is not None:
        improvement = final_health - initial_health

    if final_report:
        if get_status(final_report) in {"HEALTHY", "WARNING"}:
            recovery_status = "RECOVERED"
        else:
            recovery_status = "HEALING REQUIRED"
    else:
        recovery_status = "HEALING REQUIRED"

    stories = [
        normalize_story(story)
        for story in extract_stories(repaired_data)
    ]

    return {
        "initial_report": initial_report,
        "final_report": final_report,
        "initial_health": initial_health,
        "final_health": final_health,
        "initial_records": initial_records,
        "final_records": final_records,
        "baseline_records": baseline_records,
        "initial_deviation": initial_deviation,
        "final_deviation": final_deviation,
        "improvement": improvement,
        "recovery_status": recovery_status,
        "critical_issues": get_critical_issues(initial_report),
        "warnings": get_warnings(initial_report),
        "stories": stories,
    }