from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from .brightdata_client import approve_heal, heal_scraper, run_scraper
from .orchestrator import build_healing_prompt, evaluate_extraction


@dataclass
class RecoveryResult:
    status: str
    initial_health: float
    final_health: float | None
    healing_attempted: bool
    approval_required: bool
    scraper_repaired: bool
    recovery_verified: bool
    reasons: list[str] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "initial_health": self.initial_health,
            "final_health": self.final_health,
            "healing_attempted": self.healing_attempted,
            "approval_required": self.approval_required,
            "scraper_repaired": self.scraper_repaired,
            "recovery_verified": self.recovery_verified,
            "reasons": self.reasons,
            "steps": self.steps,
        }


def _status_from_heal_result(result: Any) -> str:
    if not isinstance(result, dict):
        return ""

    return str(result.get("status", "")).lower()


def repair_extraction(
    collector_id: str,
    current_path: Path,
    baseline_path: Path,
    healed_output_path: Path,
    heal_output_path: Path,
    approve_output_path: Path,
    scraper_url: str,
    *,
    run_scraper_fn: Callable = run_scraper,
    heal_scraper_fn: Callable = heal_scraper,
    approve_heal_fn: Callable = approve_heal,
) -> RecoveryResult:

    report, decision, _ = evaluate_extraction(
        current_path,
        baseline_path,
    )

    steps = [
        "Evaluate current extraction health.",
    ]

    if decision.action == "none":
        steps.append("No healing required.")

        return RecoveryResult(
            status="healthy",
            initial_health=report.health_score,
            final_health=report.health_score,
            healing_attempted=False,
            approval_required=False,
            scraper_repaired=False,
            recovery_verified=True,
            reasons=[],
            steps=steps,
        )

    if decision.action == "investigate":
        steps.append(
            "Investigation required; automatic scraper repair was not triggered."
        )

        return RecoveryResult(
            status="investigation_required",
            initial_health=report.health_score,
            final_health=None,
            healing_attempted=False,
            approval_required=False,
            scraper_repaired=False,
            recovery_verified=False,
            reasons=decision.reasons.copy(),
            steps=steps,
        )

    prompt = build_healing_prompt(report)

    steps.append("Generate a targeted Bright Data healing prompt.")
    steps.append("Request a Bright Data scraper repair.")

    heal_result = heal_scraper_fn(
        collector_id=collector_id,
        prompt=prompt,
        url=scraper_url,
        output_path=heal_output_path,
    )

    healing_status = _status_from_heal_result(heal_result)

    if healing_status in {
        "awaiting_approval",
        "pending_approval",
        "approval_required",
    }:
        steps.append("Bright Data repair is awaiting approval.")

        return RecoveryResult(
            status="awaiting_approval",
            initial_health=report.health_score,
            final_health=None,
            healing_attempted=True,
            approval_required=True,
            scraper_repaired=False,
            recovery_verified=False,
            reasons=decision.reasons.copy(),
            steps=steps,
        )

    if healing_status not in {"done", "completed", "success", "succeeded"}:
        steps.append("Bright Data healing did not complete successfully.")

        return RecoveryResult(
            status="repair_failed",
            initial_health=report.health_score,
            final_health=None,
            healing_attempted=True,
            approval_required=False,
            scraper_repaired=False,
            recovery_verified=False,
            reasons=decision.reasons.copy(),
            steps=steps,
        )

    steps.append("Bright Data repair completed.")
    steps.append("Re-run the repaired scraper.")

    run_scraper_fn(
        collector_id=collector_id,
        url=scraper_url,
        output_path=healed_output_path,
    )

    steps.append("Validate the repaired extraction against the baseline.")

    final_report, _, _ = evaluate_extraction(
        healed_output_path,
        baseline_path,
    )

    if final_report.status in {"healthy", "warning"} and not final_report.critical_issues:
        steps.append("Repaired extraction passed validation.")

        return RecoveryResult(
            status="recovered",
            initial_health=report.health_score,
            final_health=final_report.health_score,
            healing_attempted=True,
            approval_required=False,
            scraper_repaired=True,
            recovery_verified=True,
            reasons=decision.reasons.copy(),
            steps=steps,
        )

    steps.append("Repaired extraction failed post-repair validation.")

    return RecoveryResult(
        status="verification_failed",
        initial_health=report.health_score,
        final_health=final_report.health_score,
        healing_attempted=True,
        approval_required=False,
        scraper_repaired=True,
        recovery_verified=False,
        reasons=decision.reasons.copy(),
        steps=steps,
    )


def approve_and_verify_repair(
    collector_id: str,
    baseline_path: Path,
    healed_output_path: Path,
    approve_output_path: Path,
    scraper_url: str,
    *,
    initial_health: float = 0.0,
    approve_heal_fn: Callable = approve_heal,
    run_scraper_fn: Callable = run_scraper,
) -> RecoveryResult:

    steps = [
        "Approve the pending Bright Data scraper repair.",
    ]

    approve_result = approve_heal_fn(
        collector_id=collector_id,
        url=scraper_url,
        output_path=approve_output_path,
    )

    approval_status = _status_from_heal_result(approve_result)

    if approval_status not in {
        "done",
        "completed",
        "success",
        "succeeded",
    }:
        return RecoveryResult(
            status="repair_failed",
            initial_health=initial_health,
            final_health=None,
            healing_attempted=True,
            approval_required=True,
            scraper_repaired=False,
            recovery_verified=False,
            reasons=["approval_failed"],
            steps=steps,
        )

    steps.append("Repair approved successfully.")
    steps.append("Re-run the repaired scraper.")

    run_scraper_fn(
        collector_id=collector_id,
        url=scraper_url,
        output_path=healed_output_path,
    )

    steps.append("Validate the repaired extraction against the baseline.")

    final_report, _, _ = evaluate_extraction(
        healed_output_path,
        baseline_path,
    )

    validation_passed = (
        final_report.status == "healthy"
        or (
            final_report.status == "warning"
            and not getattr(final_report, "critical_issues", [])
        )
    )

    if validation_passed:
        steps.append("Repaired extraction passed validation.")

        return RecoveryResult(
            status="recovered",
            initial_health=initial_health,
            final_health=final_report.health_score,
            healing_attempted=True,
            approval_required=True,
            scraper_repaired=True,
            recovery_verified=True,
            reasons=[],
            steps=steps,
        )

    steps.append("Repaired extraction failed post-repair validation.")

    return RecoveryResult(
        status="verification_failed",
        initial_health=initial_health,
        final_health=final_report.health_score,
        healing_attempted=True,
        approval_required=True,
        scraper_repaired=True,
        recovery_verified=False,
        reasons=["post_repair_validation_failed"],
        steps=steps,
    )
