from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from .models import RecoveryEvidence

@dataclass
class RecoverySummary:
    """
    Aggregated operational summary for a collector's recovery history.
    """

    collector_id: str
    total_runs: int
    successful_recoveries: int
    failed_recoveries: int
    approval_required_runs: int
    healing_attempts: int
    verification_failures: int
    success_rate: float
    latest_status: str | None
    latest_state: str | None
    latest_started_at: str | None
    latest_completed_at: str | None
    average_health_improvement: float | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "collector_id": self.collector_id,
            "total_runs": self.total_runs,
            "successful_recoveries": self.successful_recoveries,
            "failed_recoveries": self.failed_recoveries,
            "approval_required_runs": self.approval_required_runs,
            "healing_attempts": self.healing_attempts,
            "verification_failures": self.verification_failures,
            "success_rate": self.success_rate,
            "latest_status": self.latest_status,
            "latest_state": self.latest_state,
            "latest_started_at": self.latest_started_at,
            "latest_completed_at": self.latest_completed_at,
            "average_health_improvement": self.average_health_improvement,
        }

@dataclass
class RecoveryRun:
    """
    Persistent record describing one completed recovery operation.

    RecoveryRun is intentionally separate from RecoveryEvidence:
    evidence describes what happened inside the recovery workflow,
    while this run provides a persistent operational record.
    """

    run_id: str
    collector_id: str
    target_url: str
    started_at: str
    completed_at: str
    initial_health: float
    final_health: float | None
    state: str
    status: str
    healing_attempted: bool
    approval_required: bool
    scraper_repaired: bool
    recovery_verified: bool
    reasons: list[str] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)
    state_history: list[str] = field(default_factory=list)
    evidence: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "collector_id": self.collector_id,
            "target_url": self.target_url,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "initial_health": self.initial_health,
            "final_health": self.final_health,
            "state": self.state,
            "status": self.status,
            "healing_attempted": self.healing_attempted,
            "approval_required": self.approval_required,
            "scraper_repaired": self.scraper_repaired,
            "recovery_verified": self.recovery_verified,
            "reasons": self.reasons,
            "steps": self.steps,
            "state_history": self.state_history,
            "evidence": self.evidence,
        }

    @classmethod
    def from_evidence(
        cls,
        evidence: RecoveryEvidence,
        *,
        initial_health: float,
        final_health: float | None,
        started_at: str,
        completed_at: str,
        run_id: str | None = None,
    ) -> "RecoveryRun":
        return cls(
            run_id=run_id or str(uuid4()),
            collector_id=evidence.collector_id,
            target_url=evidence.target_url,
            started_at=started_at,
            completed_at=completed_at,
            initial_health=initial_health,
            final_health=final_health,
            state=evidence.state.value,
            status=evidence.status,
            healing_attempted=evidence.healing_attempted,
            approval_required=evidence.approval_required,
            scraper_repaired=evidence.scraper_repaired,
            recovery_verified=evidence.recovery_verified,
            reasons=evidence.reasons.copy(),
            steps=evidence.steps.copy(),
            state_history=evidence.state_history.copy(),
            evidence=evidence.to_dict(),
        )


class RecoveryHistoryStore:
    """
    JSON-backed persistent store for recovery runs.

    Each collector gets its own history file:

        <root>/<collector_id>.json

    The format is intentionally simple so it can later be migrated
    to SQLite, PostgreSQL, or another durable store without changing
    the recovery engine's public API.
    """

    def __init__(self, root_path: Path):
        self.root_path = Path(root_path)

    def _collector_path(self, collector_id: str) -> Path:
        return self.root_path / f"{collector_id}.json"

    def _read_runs(self, collector_id: str) -> list[dict[str, Any]]:
        path = self._collector_path(collector_id)

        if not path.exists():
            return []

        raw = json.loads(
            path.read_text(encoding="utf-8")
        )

        if not isinstance(raw, list):
            raise ValueError(
                f"Recovery history must contain a JSON list: {path}"
            )

        return raw

    def append(self, run: RecoveryRun) -> None:
        runs = self._read_runs(run.collector_id)
        runs.append(run.to_dict())

        self.root_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._collector_path(
            run.collector_id
        ).write_text(
            json.dumps(
                runs,
                indent=2,
                ensure_ascii=False,
            ) + "\n",
            encoding="utf-8",
        )

    def list_runs(
        self,
        collector_id: str,
    ) -> list[dict[str, Any]]:
        return self._read_runs(collector_id)

    def latest(
        self,
        collector_id: str,
    ) -> dict[str, Any] | None:
        runs = self._read_runs(collector_id)

        if not runs:
            return None

        return runs[-1]

    def summarize(
        self,
        collector_id: str,
    ) -> RecoverySummary:
        """
        Return aggregated recovery statistics for a collector.
        """
        runs = self._read_runs(collector_id)

        if not runs:
            return RecoverySummary(
                collector_id=collector_id,
                total_runs=0,
                successful_recoveries=0,
                failed_recoveries=0,
                approval_required_runs=0,
                healing_attempts=0,
                verification_failures=0,
                success_rate=0.0,
                latest_status=None,
                latest_state=None,
                latest_started_at=None,
                latest_completed_at=None,
                average_health_improvement=None,
            )

        total_runs = len(runs)

        successful_recoveries = sum(
            1
            for run in runs
            if run.get("status") == "recovered"
        )

        failed_recoveries = sum(
            1
            for run in runs
            if run.get("status")
            in {
                "repair_failed",
                "verification_failed",
                "investigation_required",
            }
        )

        approval_required_runs = sum(
            1
            for run in runs
            if run.get("approval_required") is True
        )

        healing_attempts = sum(
            1
            for run in runs
            if run.get("healing_attempted") is True
        )

        verification_failures = sum(
            1
            for run in runs
            if run.get("status") == "verification_failed"
        )

        success_rate = (
            successful_recoveries / total_runs * 100.0
        )

        health_deltas = [
            run["final_health"] - run["initial_health"]
            for run in runs
            if run.get("initial_health") is not None
            and run.get("final_health") is not None
        ]

        average_health_improvement = (
            sum(health_deltas) / len(health_deltas)
            if health_deltas
            else None
        )

        latest = runs[-1]

        return RecoverySummary(
            collector_id=collector_id,
            total_runs=total_runs,
            successful_recoveries=successful_recoveries,
            failed_recoveries=failed_recoveries,
            approval_required_runs=approval_required_runs,
            healing_attempts=healing_attempts,
            verification_failures=verification_failures,
            success_rate=success_rate,
            latest_status=latest.get("status"),
            latest_state=latest.get("state"),
            latest_started_at=latest.get("started_at"),
            latest_completed_at=latest.get("completed_at"),
            average_health_improvement=average_health_improvement,
        )


def utc_now() -> str:
    """
    Return the current UTC timestamp in ISO-8601 format.
    """
    return datetime.now(timezone.utc).isoformat()