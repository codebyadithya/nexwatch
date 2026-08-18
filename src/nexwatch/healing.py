from dataclasses import dataclass, field

from .models import HealthReport


@dataclass
class HealingDecision:
    action: str
    severity: str
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "severity": self.severity,
            "reasons": self.reasons,
        }


@dataclass
class HealingPlan:
    action: str
    severity: str
    reasons: list[str] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "severity": self.severity,
            "reasons": self.reasons,
            "steps": self.steps,
        }


def decide_healing(report: HealthReport) -> HealingDecision:
    if report.status == "critical":
        reasons = []

        if report.record_count_deviation_percent >= 25.0:
            reasons.append("record_count_drift")

        if report.invalid_url_count > 0:
            reasons.append("invalid_url")

        if report.duplicate_count > 0:
            reasons.append("duplicate_records")

        if not reasons:
            reasons.append("critical_health_status")

        return HealingDecision(
            action="heal",
            severity="critical",
            reasons=reasons,
        )

    if report.status == "warning":
        return HealingDecision(
            action="investigate",
            severity="warning",
            reasons=[
                "non_critical_data_quality_issue"
            ],
        )

    return HealingDecision(
        action="none",
        severity="healthy",
        reasons=[],
    )


def build_healing_plan(
    report: HealthReport,
    decision: HealingDecision,
) -> HealingPlan:

    if decision.action == "none":
        return HealingPlan(
            action="none",
            severity="healthy",
            reasons=[],
            steps=[
                "No healing required.",
            ],
        )

    if decision.action == "investigate":
        return HealingPlan(
            action="investigate",
            severity="warning",
            reasons=decision.reasons.copy(),
            steps=[
                "Inspect extraction health warnings.",
                "Review affected fields and data-quality signals.",
                "Do not trigger automatic scraper repair.",
            ],
        )

    steps = [
        "Record the detected extraction failure.",
        "Request repair of the affected Bright Data scraper.",
        "Re-run the repaired scraper.",
        "Validate the repaired extraction against the data contract.",
        "Compare the repaired output against the known-good baseline.",
        "Declare recovery only if validation succeeds.",
    ]

    return HealingPlan(
        action="heal",
        severity=decision.severity,
        reasons=decision.reasons.copy(),
        steps=steps,
    )
