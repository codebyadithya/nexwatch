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