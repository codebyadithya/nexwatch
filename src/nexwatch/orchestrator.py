import json
from pathlib import Path
from typing import Any

from .brightdata_client import approve_heal, heal_scraper, run_scraper
from .healing import HealingDecision, HealingPlan, build_healing_plan, decide_healing
from .validator import validate_hacker_news


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def extract_stories(data: Any) -> list[dict]:
    if not isinstance(data, list) or not data:
        raise ValueError("Expected a non-empty scraper result list.")

    payload = data[0]

    if not isinstance(payload, dict):
        raise ValueError("Expected the first scraper result to be an object.")

    stories = payload.get("stories")

    if not isinstance(stories, list):
        raise ValueError("Expected scraper output to contain a stories array.")

    if not all(isinstance(story, dict) for story in stories):
        raise ValueError("Expected every story to be an object.")

    return stories


def build_healing_prompt(report) -> str:
    problems = []

    if report.record_count_deviation_percent >= 25.0:
        problems.append(
            "The extracted record count has drifted significantly "
            f"from the baseline ({report.record_count_deviation_percent:.2f}% deviation)."
        )

    if report.invalid_url_count > 0:
        problems.append(
            f"{report.invalid_url_count} extracted URL(s) are invalid."
        )

    for issue in report.critical_issues:
        if issue not in problems:
            problems.append(issue)

    if not problems:
        problems.append(
            "The extraction has a critical health status and requires investigation."
        )

    prompt = (
        "The Hacker News scraper extraction has degraded. "
        "Repair the scraper so it reliably extracts the required story fields "
        "(title, url, points, author) and preserves comment_count when available. "
        "Investigate the following detected problems: "
        + " ".join(problems)
        + " After repairing the scraper, ensure the extraction can be re-run "
        "and validated against the known-good baseline."
    )

    return prompt[:1000]


def run_validation(
    current_path: Path,
    baseline_path: Path,
):
    current_data = load_json(current_path)
    baseline_data = load_json(baseline_path)

    current_records = extract_stories(current_data)
    baseline_records = extract_stories(baseline_data)

    return validate_hacker_news(
        current_records=current_records,
        baseline_records=baseline_records,
    )


def evaluate_extraction(
    current_path: Path,
    baseline_path: Path,
) -> tuple[Any, HealingDecision, HealingPlan]:
    report = run_validation(
        current_path=current_path,
        baseline_path=baseline_path,
    )

    decision = decide_healing(report)

    plan = build_healing_plan(
        report=report,
        decision=decision,
    )

    return report, decision, plan


def execute_healing_cycle(
    collector_id: str,
    url: str,
    baseline_path: Path,
    current_path: Path,
    heal_output_path: Path,
    approve_output_path: Path,
    repaired_output_path: Path,
) -> dict[str, Any]:

    report, decision, plan = evaluate_extraction(
        current_path=current_path,
        baseline_path=baseline_path,
    )

    result: dict[str, Any] = {
        "initial_report": report.to_dict(),
        "decision": decision.to_dict(),
        "plan": plan.to_dict(),
    }

    if decision.action != "heal":
        result["status"] = "no_healing_executed"
        return result

    prompt = build_healing_prompt(report)

    result["healing_prompt"] = prompt

    heal_result = heal_scraper(
        collector_id=collector_id,
        prompt=prompt,
        url=url,
        output_path=heal_output_path,
    )

    result["heal_result"] = heal_result

    heal_status = (
        heal_result.get("status")
        if isinstance(heal_result, dict)
        else None
    )

    if heal_status == "awaiting_approval":
        approve_result = approve_heal(
            collector_id=collector_id,
            url=url,
            output_path=approve_output_path,
        )

        result["approve_result"] = approve_result

    repaired_result = run_scraper(
        collector_id=collector_id,
        url=url,
        output_path=repaired_output_path,
    )

    repaired_report = validate_hacker_news(
        current_records=extract_stories(repaired_result),
        baseline_records=extract_stories(load_json(baseline_path)),
    )

    result["repaired_report"] = repaired_report.to_dict()

    if repaired_report.status == "healthy":
        result["status"] = "recovered"
    else:
        result["status"] = "repair_failed_validation"

    return result
