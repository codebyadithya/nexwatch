from dataclasses import dataclass, field
from enum import Enum


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
class RecoveryContext:
    """
    Owns the lifecycle state of a single recovery operation.

    The context is intentionally small. It is responsible for
    enforcing valid state transitions and recording the transition
    history for auditability.
    """

    state: RecoveryState = RecoveryState.DETECTED
    history: list[RecoveryState] = field(
        default_factory=lambda: [RecoveryState.DETECTED]
    )

    def advance(self, target: RecoveryState) -> RecoveryState:
        """
        Move the recovery workflow to a valid next state.

        Raises:
            ValueError: if the requested transition is invalid.
        """
        self.state = transition(self.state, target)
        self.history.append(self.state)
        return self.state

    @property
    def is_terminal(self) -> bool:
        return self.state in {
            RecoveryState.RECOVERED,
            RecoveryState.FAILED,
        }

    def history_values(self) -> list[str]:
        return [state.value for state in self.history]