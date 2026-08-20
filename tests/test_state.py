import unittest

from src.nexwatch.state import (
    RecoveryContext,
    RecoveryState,
    can_transition,
    transition,
)


class RecoveryStateTests(unittest.TestCase):

    def test_valid_transition_is_allowed(self):
        self.assertTrue(
            can_transition(
                RecoveryState.DETECTED,
                RecoveryState.ASSESSED,
            )
        )

    def test_invalid_transition_is_rejected(self):
        self.assertFalse(
            can_transition(
                RecoveryState.DETECTED,
                RecoveryState.HEALING,
            )
        )

    def test_transition_function_returns_target_state(self):
        result = transition(
            RecoveryState.DETECTED,
            RecoveryState.ASSESSED,
        )

        self.assertEqual(
            result,
            RecoveryState.ASSESSED,
        )

    def test_transition_function_rejects_invalid_transition(self):
        with self.assertRaises(ValueError):
            transition(
                RecoveryState.DETECTED,
                RecoveryState.RECOVERED,
            )

    def test_context_starts_detected(self):
        context = RecoveryContext()

        self.assertEqual(
            context.state,
            RecoveryState.DETECTED,
        )

        self.assertEqual(
            context.history_values(),
            ["detected"],
        )

    def test_context_records_transition_history(self):
        context = RecoveryContext()

        context.advance(RecoveryState.ASSESSED)
        context.advance(RecoveryState.HEALING)
        context.advance(RecoveryState.VERIFYING)
        context.advance(RecoveryState.RECOVERED)

        self.assertEqual(
            context.state,
            RecoveryState.RECOVERED,
        )

        self.assertEqual(
            context.history_values(),
            [
                "detected",
                "assessed",
                "healing",
                "verifying",
                "recovered",
            ],
        )

    def test_context_rejects_invalid_transition(self):
        context = RecoveryContext()

        with self.assertRaises(ValueError):
            context.advance(RecoveryState.HEALING)

        self.assertEqual(
            context.state,
            RecoveryState.DETECTED,
        )

        self.assertEqual(
            context.history_values(),
            ["detected"],
        )

    def test_terminal_recovered_state(self):
        context = RecoveryContext()

        context.advance(RecoveryState.ASSESSED)
        context.advance(RecoveryState.RECOVERED)

        self.assertTrue(context.is_terminal)

    def test_terminal_failed_state(self):
        context = RecoveryContext()

        context.advance(RecoveryState.ASSESSED)
        context.advance(RecoveryState.FAILED)

        self.assertTrue(context.is_terminal)

    def test_non_terminal_state(self):
        context = RecoveryContext()

        context.advance(RecoveryState.ASSESSED)

        self.assertFalse(context.is_terminal)

    def test_recovered_cannot_transition_again(self):
        context = RecoveryContext()

        context.advance(RecoveryState.ASSESSED)
        context.advance(RecoveryState.RECOVERED)

        with self.assertRaises(ValueError):
            context.advance(RecoveryState.HEALING)


if __name__ == "__main__":
    unittest.main()