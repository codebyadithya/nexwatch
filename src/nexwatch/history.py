from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from .models import RecoveryEvidence


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


def utc_now() -> str:
    """
    Return the current UTC timestamp in ISO-8601 format.
    """
    return datetime.now(timezone.utc).isoformat()