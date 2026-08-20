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

    def test_recovery_event_serializes(self):
        context = RecoveryContext()

        event = context.record_event(
            "recovery_started",
            "Recovery workflow started.",
            metadata={"collector_id": "c_test"},
        )

        payload = event.to_dict()

        self.assertEqual(payload["event"], "recovery_started")
        self.assertEqual(payload["state"], "detected")
        self.assertEqual(
            payload["message"],
            "Recovery workflow started.",
        )
        self.assertEqual(
            payload["metadata"]["collector_id"],
            "c_test",
        )
        self.assertTrue(payload["timestamp"])

    def test_recovery_context_records_events_in_order(self):
        context = RecoveryContext()

        context.record_event(
            "recovery_started",
            "Recovery workflow started.",
        )
        context.advance(RecoveryState.ASSESSED)
        context.record_event(
            "assessment_completed",
            "Assessment completed.",
        )

        self.assertEqual(
            [event.event for event in context.events],
            [
                "recovery_started",
                "assessment_completed",
            ],
        )

    def test_recovery_events_capture_state_at_event_time(self):
        context = RecoveryContext()

        context.record_event(
            "recovery_started",
            "Recovery workflow started.",
        )
        context.advance(RecoveryState.ASSESSED)
        context.record_event(
            "assessment_completed",
            "Assessment completed.",
        )

        self.assertEqual(
            context.events[0].state,
            RecoveryState.DETECTED,
        )
        self.assertEqual(
            context.events[1].state,
            RecoveryState.ASSESSED,
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