import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from src.nexwatch.recovery import (
    approve_and_verify_repair,
    repair_extraction,
)
from src.nexwatch.history import RecoveryHistoryStore
from src.nexwatch.models import HealthReport
from src.nexwatch.state import RecoveryState


BASELINE = Path("data/baselines/hn-baseline-2026-08-17.json")
HEALTHY = Path("data/runs/client-test-2.json")
DEGRADED = Path("data/test-fixtures/hn-degraded.json")


class RecoveryTests(unittest.TestCase):

    def test_healthy_extraction_does_not_trigger_healing(self):
        heal_mock = Mock()

        with tempfile.TemporaryDirectory() as directory:
            result = repair_extraction(
                collector_id="c_test",
                current_path=HEALTHY,
                baseline_path=BASELINE,
                healed_output_path=Path(directory) / "healed.json",
                heal_output_path=Path(directory) / "heal.json",
                approve_output_path=Path(directory) / "approve.json",
                scraper_url="https://news.ycombinator.com",
                heal_scraper_fn=heal_mock,
            )

        self.assertEqual(result.status, "healthy")
        self.assertFalse(result.healing_attempted)
        self.assertTrue(result.recovery_verified)
        heal_mock.assert_not_called()

    def test_recovery_run_is_persisted_to_history(self):
        heal_mock = Mock()

        with tempfile.TemporaryDirectory() as directory:
            history_store = RecoveryHistoryStore(
                Path(directory) / "history"
            )
            result = repair_extraction(
                collector_id="c_test",
                current_path=HEALTHY,
                baseline_path=BASELINE,
                healed_output_path=Path(directory) / "healed.json",
                heal_output_path=Path(directory) / "heal.json",
                approve_output_path=Path(directory) / "approve.json",
                scraper_url="https://news.ycombinator.com",
                heal_scraper_fn=heal_mock,
                history_store=history_store,
            )
            runs = history_store.list_runs("c_test")

        self.assertEqual(result.status, "healthy")
        self.assertEqual(len(runs), 1)
        run = runs[0]
        self.assertEqual(run["collector_id"], "c_test")
        self.assertEqual(
            run["target_url"],
            "https://news.ycombinator.com",
        )
        self.assertEqual(run["status"], "healthy")
        self.assertEqual(run["initial_health"], result.initial_health)
        self.assertEqual(run["final_health"], result.final_health)
        self.assertEqual(
            run["state"],
            "recovered",
        )
        self.assertTrue(run["events"])
        self.assertEqual(
            run["events"][0]["event"],
            "recovery_started",
        )
        self.assertEqual(
            run["events"][-1]["event"],
            "recovery_not_required",
        )
        self.assertTrue(run["started_at"])
        self.assertTrue(run["completed_at"])
        self.assertTrue(run["run_id"])

    def test_failed_repair_is_persisted_to_history(self):
        heal_mock = Mock(
            return_value={"status": "failed"}
        )

        with tempfile.TemporaryDirectory() as directory:
            history_store = RecoveryHistoryStore(
                Path(directory) / "history"
            )
            result = repair_extraction(
                collector_id="c_test",
                current_path=DEGRADED,
                baseline_path=BASELINE,
                healed_output_path=Path(directory) / "healed.json",
                heal_output_path=Path(directory) / "heal.json",
                approve_output_path=Path(directory) / "approve.json",
                scraper_url="https://news.ycombinator.com",
                heal_scraper_fn=heal_mock,
                history_store=history_store,
            )
            runs = history_store.list_runs("c_test")

        self.assertEqual(result.status, "repair_failed")
        self.assertEqual(len(runs), 1)
        run = runs[0]
        self.assertEqual(
            run["status"],
            "repair_failed",
        )
        self.assertEqual(
            run["state"],
            "failed",
        )
        self.assertEqual(
            run["events"][-1]["event"],
            "healing_failed",
        )
        self.assertEqual(
            run["events"][-1]["state"],
            "failed",
        )
        self.assertIsNone(
            run["final_health"]
        )

    def test_healthy_recovery_records_terminal_state_history(self):
        heal_mock = Mock()

        with tempfile.TemporaryDirectory() as directory:
            result = repair_extraction(
                collector_id="c_test",
                current_path=HEALTHY,
                baseline_path=BASELINE,
                healed_output_path=Path(directory) / "healed.json",
                heal_output_path=Path(directory) / "heal.json",
                approve_output_path=Path(directory) / "approve.json",
                scraper_url="https://news.ycombinator.com",
                heal_scraper_fn=heal_mock,
            )

        self.assertEqual(
            result.evidence.state_history,
            [
                "detected",
                "assessed",
                "recovered",
            ],
        )
        heal_mock.assert_not_called()

    def test_failed_repair_records_failed_state_history(self):
        heal_mock = Mock(
            return_value={"status": "failed"}
        )

        with tempfile.TemporaryDirectory() as directory:
            result = repair_extraction(
                collector_id="c_test",
                current_path=DEGRADED,
                baseline_path=BASELINE,
                healed_output_path=Path(directory) / "healed.json",
                heal_output_path=Path(directory) / "heal.json",
                approve_output_path=Path(directory) / "approve.json",
                scraper_url="https://news.ycombinator.com",
                heal_scraper_fn=heal_mock,
            )

        self.assertEqual(result.status, "repair_failed")
        self.assertIsNotNone(result.evidence)
        self.assertEqual(
            result.evidence.state,
            RecoveryState.FAILED,
        )
        self.assertEqual(
            result.evidence.state_history,
            [
                "detected",
                "assessed",
                "healing",
                "failed",
            ],
        )

    def test_awaiting_approval_records_state_history(self):
        heal_mock = Mock(
            return_value={"status": "awaiting_approval"}
        )

        with tempfile.TemporaryDirectory() as directory:
            result = repair_extraction(
                collector_id="c_test",
                current_path=DEGRADED,
                baseline_path=BASELINE,
                healed_output_path=Path(directory) / "healed.json",
                heal_output_path=Path(directory) / "heal.json",
                approve_output_path=Path(directory) / "approve.json",
                scraper_url="https://news.ycombinator.com",
                heal_scraper_fn=heal_mock,
            )

        self.assertEqual(
            result.status,
            "awaiting_approval",
        )
        self.assertIsNotNone(result.evidence)
        self.assertEqual(
            result.evidence.state,
            RecoveryState.AWAITING_APPROVAL,
        )
        self.assertEqual(
            result.evidence.state_history,
            [
                "detected",
                "assessed",
                "healing",
                "awaiting_approval",
            ],
        )

    def test_warning_path_does_not_trigger_automatic_repair(self):
        with tempfile.TemporaryDirectory() as directory:
            current = Path(directory) / "warning.json"

            baseline_data = json.loads(BASELINE.read_text(encoding="utf-8"))

            # Remove only a small amount of data so the result remains
            # non-critical while still producing a warning-level condition.
            payload = baseline_data[0]
            payload["stories"] = payload["stories"][:27]

            current.write_text(
                json.dumps(baseline_data),
                encoding="utf-8",
            )

            heal_mock = Mock()

            result = repair_extraction(
                collector_id="c_test",
                current_path=current,
                baseline_path=BASELINE,
                healed_output_path=Path(directory) / "healed.json",
                heal_output_path=Path(directory) / "heal.json",
                approve_output_path=Path(directory) / "approve.json",
                scraper_url="https://news.ycombinator.com",
                heal_scraper_fn=heal_mock,
            )

        self.assertEqual(result.status, "investigation_required")
        self.assertFalse(result.healing_attempted)
        heal_mock.assert_not_called()

    def test_critical_extraction_stops_for_approval(self):
        heal_mock = Mock(
            return_value={"status": "awaiting_approval"}
        )

        with tempfile.TemporaryDirectory() as directory:
            result = repair_extraction(
                collector_id="c_test",
                current_path=DEGRADED,
                baseline_path=BASELINE,
                healed_output_path=Path(directory) / "healed.json",
                heal_output_path=Path(directory) / "heal.json",
                approve_output_path=Path(directory) / "approve.json",
                scraper_url="https://news.ycombinator.com",
                heal_scraper_fn=heal_mock,
            )

        self.assertEqual(result.status, "awaiting_approval")
        self.assertTrue(result.healing_attempted)
        self.assertTrue(result.approval_required)
        self.assertFalse(result.recovery_verified)

        self.assertIsNotNone(result.evidence)
        event_names = [
            event["event"]
            for event in result.evidence.events
        ]
        self.assertIn("healing_awaiting_approval", event_names)

        heal_mock.assert_called_once()

        prompt = heal_mock.call_args.kwargs["prompt"]

        self.assertIn("record count", prompt.lower())
        self.assertIn("invalid", prompt.lower())

    @patch("src.nexwatch.recovery.evaluate_extraction")
    def test_completed_repair_is_verified(self, evaluate_mock):
        initial_report = HealthReport(
            status="critical",
            health_score=68.92,
            total_records=20,
            baseline_records=30,
            record_count_deviation_percent=33.33,
            invalid_url_count=1,
            duplicate_count=0,
        )
        initial_decision = Mock(
            action="heal",
            reasons=["record_count_drift"],
        )
        initial_plan = Mock()

        final_report = HealthReport(
            status="healthy",
            health_score=100.0,
            total_records=30,
            baseline_records=30,
            record_count_deviation_percent=0.0,
            invalid_url_count=0,
            duplicate_count=0,
        )
        final_decision = Mock()
        final_plan = Mock()

        evaluate_mock.side_effect = [
            (initial_report, initial_decision, initial_plan),
            (final_report, final_decision, final_plan),
        ]

        heal_mock = Mock(
            return_value={"status": "done"}
        )

        run_mock = Mock()

        with tempfile.TemporaryDirectory() as directory:
            result = repair_extraction(
                collector_id="c_test",
                current_path=Path(directory) / "current.json",
                baseline_path=BASELINE,
                healed_output_path=Path(directory) / "healed.json",
                heal_output_path=Path(directory) / "heal.json",
                approve_output_path=Path(directory) / "approve.json",
                scraper_url="https://news.ycombinator.com",
                run_scraper_fn=run_mock,
                heal_scraper_fn=heal_mock,
            )

        self.assertEqual(result.status, "recovered")
        self.assertTrue(result.scraper_repaired)
        self.assertTrue(result.recovery_verified)
        self.assertEqual(result.initial_health, 68.92)
        self.assertEqual(result.final_health, 100.0)

        self.assertIsNotNone(result.evidence)
        events = result.evidence.events
        self.assertTrue(events)
        self.assertEqual(events[0]["event"], "recovery_started")
        event_names = [event["event"] for event in events]
        self.assertIn("assessment_completed", event_names)
        self.assertIn("healing_started", event_names)
        self.assertIn("verification_started", event_names)
        self.assertIn("verification_passed", event_names)
        self.assertLess(
            event_names.index("healing_started"),
            event_names.index("verification_started"),
        )
        self.assertLess(
            event_names.index("verification_started"),
            event_names.index("verification_passed"),
        )

        heal_mock.assert_called_once()
        run_mock.assert_called_once()

    @patch("src.nexwatch.recovery.evaluate_extraction")
    def test_repair_that_fails_validation_is_not_declared_recovered(
        self,
        evaluate_mock,
    ):
        initial_report = HealthReport(
            status="critical",
            health_score=68.92,
            total_records=20,
            baseline_records=30,
            record_count_deviation_percent=33.33,
            invalid_url_count=1,
            duplicate_count=0,
        )
        initial_decision = Mock(
            action="heal",
            reasons=["invalid_url"],
        )

        final_report = HealthReport(
            status="critical",
            health_score=70.0,
            total_records=20,
            baseline_records=30,
            record_count_deviation_percent=33.33,
            invalid_url_count=1,
            duplicate_count=0,
            critical_issues=["1 invalid source URL(s) detected."],
        )

        evaluate_mock.side_effect = [
            (initial_report, initial_decision, Mock()),
            (final_report, Mock(), Mock()),
        ]

        heal_mock = Mock(
            return_value={"status": "done"}
        )

        run_mock = Mock()

        with tempfile.TemporaryDirectory() as directory:
            result = repair_extraction(
                collector_id="c_test",
                current_path=Path(directory) / "current.json",
                baseline_path=BASELINE,
                healed_output_path=Path(directory) / "healed.json",
                heal_output_path=Path(directory) / "heal.json",
                approve_output_path=Path(directory) / "approve.json",
                scraper_url="https://news.ycombinator.com",
                run_scraper_fn=run_mock,
                heal_scraper_fn=heal_mock,
            )

        self.assertEqual(result.status, "verification_failed")
        self.assertTrue(result.scraper_repaired)
        self.assertFalse(result.recovery_verified)
        self.assertIsNotNone(result.evidence)
        events = result.evidence.events
        self.assertEqual(events[-1]["event"], "verification_failed")
        self.assertEqual(events[-1]["state"], "failed")

    @patch("src.nexwatch.recovery.evaluate_extraction")
    def test_approval_then_successful_verification(self, evaluate_mock):
        final_report = Mock(
            status="healthy",
            health_score=100.0,
        )

        evaluate_mock.return_value = (
            final_report,
            Mock(),
            Mock(),
        )

        approve_mock = Mock(
            return_value={"status": "done"}
        )

        run_mock = Mock()

        with tempfile.TemporaryDirectory() as directory:
            result = approve_and_verify_repair(
                collector_id="c_test",
                baseline_path=BASELINE,
                healed_output_path=Path(directory) / "healed.json",
                approve_output_path=Path(directory) / "approve.json",
                scraper_url="https://news.ycombinator.com",
                approve_heal_fn=approve_mock,
                run_scraper_fn=run_mock,
            )

        self.assertEqual(result.status, "recovered")
        self.assertTrue(result.approval_required)
        self.assertTrue(result.recovery_verified)
        self.assertEqual(result.final_health, 100.0)

        approve_mock.assert_called_once()
        run_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()


