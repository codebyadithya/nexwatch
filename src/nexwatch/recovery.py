from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from .brightdata_client import approve_heal, heal_scraper, run_scraper
from .models import RecoveryEvidence
from .orchestrator import build_healing_prompt, evaluate_extraction
from .state import RecoveryContext, RecoveryState


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
    evidence: RecoveryEvidence | None = None

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
            "evidence": (
                self.evidence.to_dict()
                if self.evidence is not None
                else None
            ),
        }


def _status_from_heal_result(result: Any) -> str:
    if isinstance(result, dict):
        return str(result.get("status", "")).lower()

    return str(getattr(result, "status", "")).lower()


def _build_recovery_evidence(
    collector_id: str,
    scraper_url: str,
    initial_report: Any,
    decision: Any,
    *,
    state: RecoveryState,
    state_history: list[str],
    healing_attempted: bool,
    approval_required: bool,
    scraper_repaired: bool,
    recovery_verified: bool,
    final_report: Any | None,
    status: str,
    reasons: list[str],
    steps: list[str],
) -> RecoveryEvidence:
    return RecoveryEvidence(
        collector_id=collector_id,
        target_url=scraper_url,
        state=state,
        initial_report=initial_report.to_dict(),
        decision=decision.to_dict(),
        healing_attempted=healing_attempted,
        approval_required=approval_required,
        scraper_repaired=scraper_repaired,
        recovery_verified=recovery_verified,
        final_report=(
            final_report.to_dict()
            if final_report is not None
            else None
        ),
        status=status,
        reasons=reasons.copy(),
        steps=steps.copy(),
        state_history=state_history.copy(),
    )


def repair_extraction(
    collector_id: str,
    current_path: Path,
    baseline_path: Path,
    scraper_url: str,
    *,
    healed_output_path: Path | None = None,
    heal_output_path: Path | None = None,
    approve_output_path: Path | None = None,
    approval_output_path: Path | None = None,
    repaired_output_path: Path | None = None,
    healing_fn: Callable[..., Any] = heal_scraper,
    approval_fn: Callable[..., Any] = approve_heal,
    run_fn: Callable[..., Any] = run_scraper,
    heal_scraper_fn: Callable[..., Any] | None = None,
    approve_heal_fn: Callable[..., Any] | None = None,
    run_scraper_fn: Callable[..., Any] | None = None,
) -> RecoveryResult:
    """
    Execute the NexWatch recovery workflow.

    Compatibility note:
    The public API historically used:
        healed_output_path
        approve_output_path

    The implementation also accepts:
        repaired_output_path
        approval_output_path

    This keeps existing callers and tests working while allowing the
    architecture to evolve.
    """

    if heal_scraper_fn is not None:
        healing_fn = heal_scraper_fn

    if approve_heal_fn is not None:
        approval_fn = approve_heal_fn

    if run_scraper_fn is not None:
        run_fn = run_scraper_fn

    if heal_output_path is None:
        heal_output_path = healed_output_path

    if healed_output_path is None:
        healed_output_path = heal_output_path

    if approve_output_path is None:
        approve_output_path = approval_output_path

    if approval_output_path is None:
        approval_output_path = approve_output_path

    if repaired_output_path is None:
        repaired_output_path = healed_output_path

    report, decision, plan = evaluate_extraction(
        current_path,
        baseline_path,
    )

    steps = plan.steps.copy()

    context = RecoveryContext()

    context.advance(
        RecoveryState.ASSESSED,
    )

    if decision.action == "none":
        steps.append("No healing required.")

        context.advance(
            RecoveryState.RECOVERED,
        )

        evidence = _build_recovery_evidence(
            collector_id=collector_id,
            scraper_url=scraper_url,
            initial_report=report,
            decision=decision,
            state=context.state,
            state_history=context.history_values(),
            healing_attempted=False,
            approval_required=False,
            scraper_repaired=False,
            recovery_verified=True,
            final_report=report,
            status="healthy",
            reasons=[],
            steps=steps,
        )

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
            evidence=evidence,
        )

    if decision.action == "investigate":
        steps.append(
            "Investigation required; automatic scraper repair was not triggered."
        )

        context.advance(
            RecoveryState.FAILED,
        )

        evidence = _build_recovery_evidence(
            collector_id=collector_id,
            scraper_url=scraper_url,
            initial_report=report,
            decision=decision,
            state=context.state,
            state_history=context.history_values(),
            healing_attempted=False,
            approval_required=False,
            scraper_repaired=False,
            recovery_verified=False,
            final_report=None,
            status="investigation_required",
            reasons=decision.reasons,
            steps=steps,
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
            evidence=evidence,
        )

    prompt = build_healing_prompt(report)

    context.advance(
        RecoveryState.HEALING,
    )

    heal_result = healing_fn(
        collector_id=collector_id,
        prompt=prompt,
        output_path=heal_output_path,
    )

    healing_status = _status_from_heal_result(heal_result)

    if healing_status in {
        "awaiting_approval",
        "approval_required",
        "pending_approval",
    }:
        steps.append(
            "Bright Data repair is awaiting approval."
        )

        context.advance(
            RecoveryState.AWAITING_APPROVAL,
        )

        evidence = _build_recovery_evidence(
            collector_id=collector_id,
            scraper_url=scraper_url,
            initial_report=report,
            decision=decision,
            state=context.state,
            state_history=context.history_values(),
            healing_attempted=True,
            approval_required=True,
            scraper_repaired=False,
            recovery_verified=False,
            final_report=None,
            status="awaiting_approval",
            reasons=decision.reasons,
            steps=steps,
        )

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
            evidence=evidence,
        )

    if healing_status not in {
        "done",
        "completed",
        "success",
        "succeeded",
    }:
        steps.append(
            "Bright Data healing did not complete successfully."
        )

        context.advance(
            RecoveryState.FAILED,
        )

        evidence = _build_recovery_evidence(
            collector_id=collector_id,
            scraper_url=scraper_url,
            initial_report=report,
            decision=decision,
            state=context.state,
            state_history=context.history_values(),
            healing_attempted=True,
            approval_required=False,
            scraper_repaired=False,
            recovery_verified=False,
            final_report=None,
            status="repair_failed",
            reasons=decision.reasons,
            steps=steps,
        )

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
            evidence=evidence,
        )

    steps.append("Bright Data repair completed.")

    context.advance(
        RecoveryState.VERIFYING,
    )

    healed_output_path = run_fn(
        collector_id=collector_id,
        scraper_url=scraper_url,
        output_path=repaired_output_path,
    )

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
        steps.append(
            "Repaired extraction passed validation."
        )

        context.advance(
            RecoveryState.RECOVERED,
        )

        evidence = _build_recovery_evidence(
            collector_id=collector_id,
            scraper_url=scraper_url,
            initial_report=report,
            decision=decision,
            state=context.state,
            state_history=context.history_values(),
            healing_attempted=True,
            approval_required=False,
            scraper_repaired=True,
            recovery_verified=True,
            final_report=final_report,
            status="recovered",
            reasons=decision.reasons,
            steps=steps,
        )

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
            evidence=evidence,
        )

    steps.append(
        "Repaired extraction failed post-repair validation."
    )

    context.advance(
        RecoveryState.FAILED,
    )

    evidence = _build_recovery_evidence(
        collector_id=collector_id,
        scraper_url=scraper_url,
        initial_report=report,
        decision=decision,
        state=context.state,
        state_history=context.history_values(),
        healing_attempted=True,
        approval_required=False,
        scraper_repaired=True,
        recovery_verified=False,
        final_report=final_report,
        status="verification_failed",
        reasons=decision.reasons,
        steps=steps,
    )

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
        evidence=evidence,
    )


def approve_and_verify_repair(
    collector_id: str,
    scraper_url: str,
    initial_health: float = 0.0,
    baseline_path: Path | None = None,
    healed_output_path: Path | None = None,
    *,
    approval_output_path: Path | None = None,
    approve_output_path: Path | None = None,
    approval_fn: Callable[..., Any] | None = None,
    approve_heal_fn: Callable[..., Any] | None = None,
    run_fn: Callable[..., Any] | None = None,
    run_scraper_fn: Callable[..., Any] | None = None,
) -> RecoveryResult:

    if baseline_path is None:
        raise ValueError("baseline_path is required")

    if healed_output_path is None:
        raise ValueError("healed_output_path is required")

    # Backward-compatible parameter aliases.
    if approval_fn is None:
        approval_fn = (
            approve_heal_fn
            if approve_heal_fn is not None
            else approve_heal
        )

    if run_fn is None:
        run_fn = (
            run_scraper_fn
            if run_scraper_fn is not None
            else run_scraper
        )

    if approval_output_path is None:
        approval_output_path = approve_output_path

    steps = [
        "Approve the pending Bright Data repair.",
    ]

    approval_result = approval_fn(
        collector_id=collector_id,
        output_path=approval_output_path,
    )

    approval_status = _status_from_heal_result(
        approval_result
    )

    if approval_status not in {
        "done",
        "completed",
        "success",
        "succeeded",
    }:
        steps.append(
            "Bright Data repair approval failed."
        )

        evidence = RecoveryEvidence(
            collector_id=collector_id,
            target_url=scraper_url,
            state=RecoveryState.FAILED,
            initial_report={},
            decision={},
            healing_attempted=True,
            approval_required=True,
            scraper_repaired=False,
            recovery_verified=False,
            final_report=None,
            status="repair_failed",
            reasons=["approval_failed"],
            steps=steps.copy(),
        )

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
            evidence=evidence,
        )

    steps.append("Repair approved successfully.")

    # The approved repair must now produce the repaired extraction
    # before it can be validated against the baseline.
    steps.append(
        "Run the repaired scraper before validating recovery."
    )

    repaired_result = run_fn(
        collector_id=collector_id,
        scraper_url=scraper_url,
        output_path=healed_output_path,
    )

    # Some implementations return the output path directly while
    # others write to the path supplied above.
    actual_output_path = (
        repaired_result
        if isinstance(repaired_result, (str, Path))
        else healed_output_path
    )

    steps.append(
        "Validate the repaired extraction against the baseline."
    )

    final_report, final_decision, _ = evaluate_extraction(
        Path(actual_output_path),
        baseline_path,
    )

    validation_passed = (
        final_report.status == "healthy"
        or (
            final_report.status == "warning"
            and not getattr(
                final_report,
                "critical_issues",
                [],
            )
        )
    )

    if validation_passed:
        steps.append(
            "Repaired extraction passed validation."
        )

        evidence = RecoveryEvidence(
            collector_id=collector_id,
            target_url=scraper_url,
            state=RecoveryState.RECOVERED,
            initial_report=final_report.to_dict(),
            decision=final_decision.to_dict(),
            healing_attempted=True,
            approval_required=True,
            scraper_repaired=True,
            recovery_verified=True,
            final_report=final_report.to_dict(),
            status="recovered",
            reasons=[],
            steps=steps.copy(),
        )

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
            evidence=evidence,
        )

    steps.append(
        "Repaired extraction failed post-repair validation."
    )

    evidence = RecoveryEvidence(
        collector_id=collector_id,
        target_url=scraper_url,
        state=RecoveryState.FAILED,
        initial_report=final_report.to_dict(),
        decision=final_decision.to_dict(),
        healing_attempted=True,
        approval_required=True,
        scraper_repaired=True,
        recovery_verified=False,
        final_report=final_report.to_dict(),
        status="verification_failed",
        reasons=["post_repair_validation_failed"],
        steps=steps.copy(),
    )

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
        evidence=evidence,
    )