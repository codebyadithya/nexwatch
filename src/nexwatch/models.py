from dataclasses import dataclass, field
from typing import Any

from .state import RecoveryState


@dataclass
class FieldHealth:
    name: str
    total_records: int
    present_records: int
    completeness: float
    required: bool


@dataclass
class HealthReport:
    status: str
    health_score: float
    total_records: int
    baseline_records: int
    record_count_deviation_percent: float
    invalid_url_count: int
    duplicate_count: int
    fields: list[FieldHealth] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    critical_issues: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "health_score": self.health_score,
            "records": {
                "current": self.total_records,
                "baseline": self.baseline_records,
                "deviation_percent": self.record_count_deviation_percent,
            },
            "invalid_url_count": self.invalid_url_count,
            "duplicate_count": self.duplicate_count,
            "fields": [
                {
                    "name": field.name,
                    "total_records": field.total_records,
                    "present_records": field.present_records,
                    "completeness": field.completeness,
                    "required": field.required,
                }
                for field in self.fields
            ],
            "warnings": self.warnings,
            "critical_issues": self.critical_issues,
        }


@dataclass
class RecoveryEvidence:
    collector_id: str
    target_url: str
    state: RecoveryState
    initial_report: dict[str, Any]
    decision: dict[str, Any]
    healing_attempted: bool
    approval_required: bool
    scraper_repaired: bool
    recovery_verified: bool
    final_report: dict[str, Any] | None
    status: str
    reasons: list[str] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)
    state_history: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "collector_id": self.collector_id,
            "target_url": self.target_url,
            "state": self.state.value,
            "initial_report": self.initial_report,
            "decision": self.decision,
            "healing_attempted": self.healing_attempted,
            "approval_required": self.approval_required,
            "scraper_repaired": self.scraper_repaired,
            "recovery_verified": self.recovery_verified,
            "final_report": self.final_report,
            "status": self.status,
            "reasons": self.reasons,
            "steps": self.steps,
            "state_history": self.state_history,
        }