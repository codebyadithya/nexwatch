import tempfile
import unittest
from pathlib import Path

from src.nexwatch.history import (
    RecoveryEvent,
    RecoveryHistoryStore,
)
from src.nexwatch.models import RecoveryEvidence
from src.nexwatch.state import RecoveryState


class RecoveryHistoryTests(unittest.TestCase):

    def _make_evidence(
        self,
        *,
        status="recovered",
        state=RecoveryState.RECOVERED,
        healing_attempted=True,
        approval_required=False,
        scraper_repaired=True,
        recovery_verified=True,
    ):
        return RecoveryEvidence(
            collector_id="c_test",
            target_url="https://news.ycombinator.com",
            state=state,
            initial_report={
                "status": "critical",
                "health_score": 68.92,
            },
            decision={
                "action": "heal",
                "reasons": ["record_count_drift"],
            },
            healing_attempted=healing_attempted,
            approval_required=approval_required,
            scraper_repaired=scraper_repaired,
            recovery_verified=recovery_verified,
            final_report={
                "status": "healthy",
                "health_score": 100.0,
            },
            status=status,
            reasons=["record_count_drift"],
            steps=[
                "Healing completed.",
                "Recovery verified.",
            ],
            state_history=[
                "detected",
                "assessed",
                "healing",
                "verifying",
                "recovered",
            ],
        )

    def test_event_can_be_created_from_evidence(self):
        evidence = self._make_evidence()

        event = RecoveryEvent.from_evidence(
            evidence,
            initial_health=68.92,
            final_health=100.0,
            started_at="2026-08-20T10:00:00+00:00",
            completed_at="2026-08-20T10:00:05+00:00",
            run_id="run_test_001",
        )

        self.assertEqual(
            event.run_id,
            "run_test_001",
        )

        self.assertEqual(
            event.collector_id,
            "c_test",
        )

        self.assertEqual(
            event.state,
            "recovered",
        )

        self.assertEqual(
            event.initial_health,
            68.92,
        )

        self.assertEqual(
            event.final_health,
            100.0,
        )

        self.assertTrue(
            event.recovery_verified
        )

    def test_event_serializes_to_dict(self):
        evidence = self._make_evidence()

        event = RecoveryEvent.from_evidence(
            evidence,
            initial_health=68.92,
            final_health=100.0,
            started_at="2026-08-20T10:00:00+00:00",
            completed_at="2026-08-20T10:00:05+00:00",
            run_id="run_test_002",
        )

        data = event.to_dict()

        self.assertEqual(
            data["run_id"],
            "run_test_002",
        )

        self.assertEqual(
            data["collector_id"],
            "c_test",
        )

        self.assertEqual(
            data["state_history"],
            [
                "detected",
                "assessed",
                "healing",
                "verifying",
                "recovered",
            ],
        )

        self.assertIsNotNone(
            data["evidence"]
        )

    def test_store_appends_event(self):
        evidence = self._make_evidence()

        event = RecoveryEvent.from_evidence(
            evidence,
            initial_health=68.92,
            final_health=100.0,
            started_at="2026-08-20T10:00:00+00:00",
            completed_at="2026-08-20T10:00:05+00:00",
            run_id="run_test_003",
        )

        with tempfile.TemporaryDirectory() as directory:
            store = RecoveryHistoryStore(
                Path(directory)
            )

            store.append(event)

            events = store.list_events(
                "c_test"
            )

            self.assertEqual(
                len(events),
                1,
            )

            self.assertEqual(
                events[0]["run_id"],
                "run_test_003",
            )

    def test_store_preserves_multiple_events(self):
        evidence = self._make_evidence()

        event_one = RecoveryEvent.from_evidence(
            evidence,
            initial_health=68.92,
            final_health=100.0,
            started_at="2026-08-20T10:00:00+00:00",
            completed_at="2026-08-20T10:00:05+00:00",
            run_id="run_test_004",
        )

        event_two = RecoveryEvent.from_evidence(
            evidence,
            initial_health=72.0,
            final_health=100.0,
            started_at="2026-08-21T10:00:00+00:00",
            completed_at="2026-08-21T10:00:04+00:00",
            run_id="run_test_005",
        )

        with tempfile.TemporaryDirectory() as directory:
            store = RecoveryHistoryStore(
                Path(directory)
            )

            store.append(event_one)
            store.append(event_two)

            events = store.list_events(
                "c_test"
            )

            self.assertEqual(
                len(events),
                2,
            )

            self.assertEqual(
                events[0]["run_id"],
                "run_test_004",
            )

            self.assertEqual(
                events[1]["run_id"],
                "run_test_005",
            )

    def test_latest_returns_most_recent_event(self):
        evidence = self._make_evidence()

        event_one = RecoveryEvent.from_evidence(
            evidence,
            initial_health=68.92,
            final_health=100.0,
            started_at="2026-08-20T10:00:00+00:00",
            completed_at="2026-08-20T10:00:05+00:00",
            run_id="run_test_006",
        )

        event_two = RecoveryEvent.from_evidence(
            evidence,
            initial_health=72.0,
            final_health=100.0,
            started_at="2026-08-21T10:00:00+00:00",
            completed_at="2026-08-21T10:00:04+00:00",
            run_id="run_test_007",
        )

        with tempfile.TemporaryDirectory() as directory:
            store = RecoveryHistoryStore(
                Path(directory)
            )

            store.append(event_one)
            store.append(event_two)

            latest = store.latest(
                "c_test"
            )

            self.assertIsNotNone(latest)

            self.assertEqual(
                latest["run_id"],
                "run_test_007",
            )

    def test_latest_returns_none_when_history_does_not_exist(self):
        with tempfile.TemporaryDirectory() as directory:
            store = RecoveryHistoryStore(
                Path(directory)
            )

            self.assertIsNone(
                store.latest("unknown_collector")
            )

    def test_collectors_have_separate_history(self):
        evidence = self._make_evidence()

        event = RecoveryEvent.from_evidence(
            evidence,
            initial_health=68.92,
            final_health=100.0,
            started_at="2026-08-20T10:00:00+00:00",
            completed_at="2026-08-20T10:00:05+00:00",
            run_id="run_test_008",
        )

        with tempfile.TemporaryDirectory() as directory:
            store = RecoveryHistoryStore(
                Path(directory)
            )

            store.append(event)

            self.assertEqual(
                len(store.list_events("c_test")),
                1,
            )

            self.assertEqual(
                len(store.list_events("another_collector")),
                0,
            )


if __name__ == "__main__":
    unittest.main()