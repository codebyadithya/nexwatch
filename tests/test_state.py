import unittest

from src.nexwatch.state import (
    RecoveryState,
    can_transition,
    transition,
)


class RecoveryStateTests(unittest.TestCase):

    def test_detected_can_move_to_assessed(self):
        self.assertTrue(
            can_transition(
                RecoveryState.DETECTED,
                RecoveryState.ASSESSED,
            )
        )

    def test_assessed_can_move_to_healing(self):
        self.assertTrue(
            can_transition(
                RecoveryState.ASSESSED,
                RecoveryState.HEALING,
            )
        )

    def test_healing_can_move_to_verifying(self):
        self.assertTrue(
            can_transition(
                RecoveryState.HEALING,
                RecoveryState.VERIFYING,
            )
        )

    def test_healing_can_wait_for_approval(self):
        self.assertTrue(
            can_transition(
                RecoveryState.HEALING,
                RecoveryState.AWAITING_APPROVAL,
            )
        )

    def test_verifying_can_move_to_recovered(self):
        self.assertTrue(
            can_transition(
                RecoveryState.VERIFYING,
                RecoveryState.RECOVERED,
            )
        )

    def test_verifying_can_move_to_failed(self):
        self.assertTrue(
            can_transition(
                RecoveryState.VERIFYING,
                RecoveryState.FAILED,
            )
        )

    def test_recovered_is_terminal(self):
        self.assertFalse(
            can_transition(
                RecoveryState.RECOVERED,
                RecoveryState.HEALING,
            )
        )

    def test_failed_is_terminal(self):
        self.assertFalse(
            can_transition(
                RecoveryState.FAILED,
                RecoveryState.HEALING,
            )
        )

    def test_invalid_transition_raises(self):
        with self.assertRaises(ValueError):
            transition(
                RecoveryState.DETECTED,
                RecoveryState.RECOVERED,
            )

    def test_valid_transition_returns_target_state(self):
        result = transition(
            RecoveryState.DETECTED,
            RecoveryState.ASSESSED,
        )

        self.assertEqual(
            result,
            RecoveryState.ASSESSED,
        )


if __name__ == "__main__":
    unittest.main()