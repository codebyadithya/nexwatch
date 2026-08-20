import tempfile
import unittest
from pathlib import Path

from src.nexwatch.history import (
    RecoveryRun,
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

        event = RecoveryRun.from_evidence(
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

        event = RecoveryRun.from_evidence(
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

        event = RecoveryRun.from_evidence(
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

            runs = store.list_runs(
                "c_test"
            )

            self.assertEqual(
                len(runs),
                1,
            )

            self.assertEqual(
                runs[0]["run_id"],
                "run_test_003",
            )

    def test_store_preserves_multiple_runs(self):
        evidence = self._make_evidence()

        event_one = RecoveryRun.from_evidence(
            evidence,
            initial_health=68.92,
            final_health=100.0,
            started_at="2026-08-20T10:00:00+00:00",
            completed_at="2026-08-20T10:00:05+00:00",
            run_id="run_test_004",
        )

        event_two = RecoveryRun.from_evidence(
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

            runs = store.list_runs(
                "c_test"
            )

            self.assertEqual(
                len(runs),
                2,
            )

            self.assertEqual(
                runs[0]["run_id"],
                "run_test_004",
            )

            self.assertEqual(
                runs[1]["run_id"],
                "run_test_005",
            )

    def test_latest_returns_most_recent_run(self):
        evidence = self._make_evidence()

        event_one = RecoveryRun.from_evidence(
            evidence,
            initial_health=68.92,
            final_health=100.0,
            started_at="2026-08-20T10:00:00+00:00",
            completed_at="2026-08-20T10:00:05+00:00",
            run_id="run_test_006",
        )

        event_two = RecoveryRun.from_evidence(
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

        event = RecoveryRun.from_evidence(
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
                len(store.list_runs("c_test")),
                1,
            )

            self.assertEqual(
                len(store.list_runs("another_collector")),
                0,
            )

    def test_summary_for_empty_history(self):
        with tempfile.TemporaryDirectory() as directory:
            store = RecoveryHistoryStore(
                Path(directory)
            )

            summary = store.summarize(
                "unknown_collector"
            )

            self.assertEqual(
                summary.collector_id,
                "unknown_collector",
            )

            self.assertEqual(
                summary.total_runs,
                0,
            )

            self.assertEqual(
                summary.successful_recoveries,
                0,
            )

            self.assertEqual(
                summary.failed_recoveries,
                0,
            )

            self.assertEqual(
                summary.success_rate,
                0.0,
            )

            self.assertIsNone(
                summary.latest_status
            )

            self.assertIsNone(
                summary.average_health_improvement
            )

    def test_summary_counts_recovery_outcomes(self):
        evidence = self._make_evidence()

        successful_run = RecoveryRun.from_evidence(
            evidence,
            initial_health=60.0,
            final_health=100.0,
            started_at="2026-08-20T10:00:00+00:00",
            completed_at="2026-08-20T10:00:05+00:00",
            run_id="summary_success",
        )

        failed_evidence = self._make_evidence(
            status="verification_failed",
            state=RecoveryState.FAILED,
            healing_attempted=True,
            approval_required=False,
            scraper_repaired=True,
            recovery_verified=False,
        )

        failed_run = RecoveryRun.from_evidence(
            failed_evidence,
            initial_health=80.0,
            final_health=70.0,
            started_at="2026-08-20T11:00:00+00:00",
            completed_at="2026-08-20T11:00:05+00:00",
            run_id="summary_failure",
        )

        with tempfile.TemporaryDirectory() as directory:
            store = RecoveryHistoryStore(
                Path(directory)
            )

            store.append(successful_run)
            store.append(failed_run)

            summary = store.summarize(
                "c_test"
            )

            self.assertEqual(
                summary.total_runs,
                2,
            )

            self.assertEqual(
                summary.successful_recoveries,
                1,
            )

            self.assertEqual(
                summary.failed_recoveries,
                1,
            )

            self.assertEqual(
                summary.verification_failures,
                1,
            )

            self.assertEqual(
                summary.healing_attempts,
                2,
            )

            self.assertEqual(
                summary.success_rate,
                50.0,
            )

    def test_summary_counts_approval_required_runs(self):
        evidence = self._make_evidence(
            approval_required=True,
            scraper_repaired=False,
            recovery_verified=False,
            state=RecoveryState.AWAITING_APPROVAL,
            status="approval_required",
        )

        run = RecoveryRun.from_evidence(
            evidence,
            initial_health=68.0,
            final_health=None,
            started_at="2026-08-20T12:00:00+00:00",
            completed_at="2026-08-20T12:00:01+00:00",
            run_id="summary_approval",
        )

        with tempfile.TemporaryDirectory() as directory:
            store = RecoveryHistoryStore(
                Path(directory)
            )

            store.append(run)

            summary = store.summarize(
                "c_test"
            )

            self.assertEqual(
                summary.approval_required_runs,
                1,
            )

            self.assertEqual(
                summary.healing_attempts,
                1,
            )

    def test_summary_calculates_average_health_improvement(self):
        evidence = self._make_evidence()

        run_one = RecoveryRun.from_evidence(
            evidence,
            initial_health=60.0,
            final_health=100.0,
            started_at="2026-08-20T10:00:00+00:00",
            completed_at="2026-08-20T10:00:05+00:00",
            run_id="summary_health_001",
        )

        run_two = RecoveryRun.from_evidence(
            evidence,
            initial_health=80.0,
            final_health=90.0,
            started_at="2026-08-20T11:00:00+00:00",
            completed_at="2026-08-20T11:00:05+00:00",
            run_id="summary_health_002",
        )

        with tempfile.TemporaryDirectory() as directory:
            store = RecoveryHistoryStore(
                Path(directory)
            )

            store.append(run_one)
            store.append(run_two)

            summary = store.summarize(
                "c_test"
            )

            self.assertEqual(
                summary.average_health_improvement,
                25.0,
            )

    def test_summary_exposes_latest_run(self):
        evidence = self._make_evidence()

        run = RecoveryRun.from_evidence(
            evidence,
            initial_health=72.0,
            final_health=100.0,
            started_at="2026-08-21T10:00:00+00:00",
            completed_at="2026-08-21T10:00:04+00:00",
            run_id="summary_latest",
        )

        with tempfile.TemporaryDirectory() as directory:
            store = RecoveryHistoryStore(
                Path(directory)
            )

            store.append(run)

            summary = store.summarize(
                "c_test"
            )

            self.assertEqual(
                summary.latest_status,
                "recovered",
            )

            self.assertEqual(
                summary.latest_state,
                "recovered",
            )

            self.assertEqual(
                summary.latest_started_at,
                "2026-08-21T10:00:00+00:00",
            )

            self.assertEqual(
                summary.latest_completed_at,
                "2026-08-21T10:00:04+00:00",
            )

    def test_summary_serializes_to_dict(self):
        evidence = self._make_evidence()

        run = RecoveryRun.from_evidence(
            evidence,
            initial_health=70.0,
            final_health=100.0,
            started_at="2026-08-20T10:00:00+00:00",
            completed_at="2026-08-20T10:00:05+00:00",
            run_id="summary_dict",
        )

        with tempfile.TemporaryDirectory() as directory:
            store = RecoveryHistoryStore(
                Path(directory)
            )

            store.append(run)

            summary = store.summarize(
                "c_test"
            )

            data = summary.to_dict()

            self.assertEqual(
                data["collector_id"],
                "c_test",
            )

            self.assertEqual(
                data["total_runs"],
                1,
            )

            self.assertEqual(
                data["successful_recoveries"],
                1,
            )

            self.assertEqual(
                data["success_rate"],
                100.0,
            )


if __name__ == "__main__":
    unittest.main()