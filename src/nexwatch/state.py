from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class RecoveryState(str, Enum):
    DETECTED = "detected"
    ASSESSED = "assessed"
    HEALING = "healing"
    AWAITING_APPROVAL = "awaiting_approval"
    VERIFYING = "verifying"
    RECOVERED = "recovered"
    FAILED = "failed"


ALLOWED_TRANSITIONS = {
    RecoveryState.DETECTED: {
        RecoveryState.ASSESSED,
    },
    RecoveryState.ASSESSED: {
        RecoveryState.HEALING,
        RecoveryState.RECOVERED,
        RecoveryState.FAILED,
    },
    RecoveryState.HEALING: {
        RecoveryState.AWAITING_APPROVAL,
        RecoveryState.VERIFYING,
        RecoveryState.FAILED,
    },
    RecoveryState.AWAITING_APPROVAL: {
        RecoveryState.VERIFYING,
        RecoveryState.FAILED,
    },
    RecoveryState.VERIFYING: {
        RecoveryState.RECOVERED,
        RecoveryState.FAILED,
    },
    RecoveryState.RECOVERED: set(),
    RecoveryState.FAILED: set(),
}


def can_transition(
    current: RecoveryState,
    target: RecoveryState,
) -> bool:
    return target in ALLOWED_TRANSITIONS.get(current, set())


def transition(
    current: RecoveryState,
    target: RecoveryState,
) -> RecoveryState:
    if not can_transition(current, target):
        raise ValueError(
            f"Invalid recovery transition: "
            f"{current.value} -> {target.value}"
        )

    return target


@dataclass
class RecoveryEvent:
    """
    Immutable-style record of a meaningful recovery lifecycle event.
    """

    event: str
    state: RecoveryState
    message: str
    timestamp: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event": self.event,
            "state": self.state.value,
            "message": self.message,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


@dataclass
class RecoveryContext:
    """
    Owns the lifecycle state of a single recovery operation.

    The context is responsible for:
    - enforcing valid state transitions
    - recording state history
    - recording a chronological recovery event timeline
    """

    state: RecoveryState = RecoveryState.DETECTED
    history: list[RecoveryState] = field(
        default_factory=lambda: [RecoveryState.DETECTED]
    )
    events: list[RecoveryEvent] = field(default_factory=list)

    def advance(self, target: RecoveryState) -> RecoveryState:
        """
        Move the recovery workflow to a valid next state.

        Raises:
            ValueError: if the requested transition is invalid.
        """
        self.state = transition(self.state, target)
        self.history.append(self.state)
        return self.state

    def record_event(
        self,
        event: str,
        message: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> RecoveryEvent:
        """
        Record a chronological event associated with the current state.
        """
        recovery_event = RecoveryEvent(
            event=event,
            state=self.state,
            message=message,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata=metadata or {},
        )
        self.events.append(recovery_event)
        return recovery_event

    @property
    def is_terminal(self) -> bool:
        return self.state in {
            RecoveryState.RECOVERED,
            RecoveryState.FAILED,
        }

    def history_values(self) -> list[str]:
        return [state.value for state in self.history]

    def events_to_dict(self) -> list[dict[str, Any]]:
        return [event.to_dict() for event in self.events]