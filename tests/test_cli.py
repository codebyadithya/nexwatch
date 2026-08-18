import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.nexwatch.cli import main


BASELINE = Path("data/baselines/hn-baseline-2026-08-17.json")
HEALTHY = Path("data/runs/client-test-2.json")
DEGRADED = Path("data/test-fixtures/hn-degraded.json")


class CLITests(unittest.TestCase):

    def test_validate_healthy_extraction(self):
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "report.json"

            with patch(
                "sys.argv",
                [
                    "nexwatch",
                    "validate",
                    "--current",
                    str(HEALTHY),
                    "--baseline",
                    str(BASELINE),
                    "--output",
                    str(output_path),
                ],
            ):
                result = main()

            self.assertEqual(result, 0)
            self.assertTrue(output_path.exists())

            report = json.loads(
                output_path.read_text(encoding="utf-8")
            )

            self.assertEqual(
                report["report"]["status"],
                "healthy",
            )
            self.assertEqual(
                report["decision"]["action"],
                "none",
            )
            self.assertEqual(
                report["plan"]["action"],
                "none",
            )

    def test_validate_degraded_extraction_requests_healing(self):
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "report.json"

            with patch(
                "sys.argv",
                [
                    "nexwatch",
                    "validate",
                    "--current",
                    str(DEGRADED),
                    "--baseline",
                    str(BASELINE),
                    "--output",
                    str(output_path),
                ],
            ):
                result = main()

            self.assertEqual(result, 0)

            report = json.loads(
                output_path.read_text(encoding="utf-8")
            )

            self.assertEqual(
                report["report"]["status"],
                "critical",
            )
            self.assertEqual(
                report["decision"]["action"],
                "heal",
            )
            self.assertEqual(
                report["plan"]["action"],
                "heal",
            )

            self.assertIn(
                "record_count_drift",
                report["decision"]["reasons"],
            )

            self.assertIn(
                "invalid_url",
                report["decision"]["reasons"],
            )

    @patch("src.nexwatch.cli.repair_extraction")
    def test_recover_command_serializes_recovery_result(
        self,
        repair_mock,
    ):
        from src.nexwatch.recovery import RecoveryResult

        repair_mock.return_value = RecoveryResult(
            status="recovered",
            initial_health=68.92,
            final_health=100.0,
            healing_attempted=True,
            approval_required=False,
            scraper_repaired=True,
            recovery_verified=True,
            reasons=["record_count_drift"],
            steps=["Repair completed.", "Recovery verified."],
        )

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "recovery.json"

            with patch(
                "sys.argv",
                [
                    "nexwatch",
                    "recover",
                    "--collector-id",
                    "c_test",
                    "--url",
                    "https://news.ycombinator.com",
                    "--current",
                    str(DEGRADED),
                    "--baseline",
                    str(BASELINE),
                    "--heal-output",
                    str(Path(directory) / "heal.json"),
                    "--approve-output",
                    str(Path(directory) / "approve.json"),
                    "--repaired-output",
                    str(Path(directory) / "repaired.json"),
                    "--output",
                    str(output_path),
                ],
            ):
                result = main()

            self.assertEqual(result, 0)
            self.assertTrue(output_path.exists())

            report = json.loads(
                output_path.read_text(encoding="utf-8")
            )

            self.assertEqual(
                report["status"],
                "recovered",
            )
            self.assertEqual(
                report["initial_health"],
                68.92,
            )
            self.assertEqual(
                report["final_health"],
                100.0,
            )
            self.assertTrue(
                report["recovery_verified"]
            )

            repair_mock.assert_called_once()

    @patch("src.nexwatch.cli.repair_extraction")
    def test_recover_command_returns_failure_for_failed_recovery(
        self,
        repair_mock,
    ):
        from src.nexwatch.recovery import RecoveryResult

        repair_mock.return_value = RecoveryResult(
            status="verification_failed",
            initial_health=68.92,
            final_health=70.0,
            healing_attempted=True,
            approval_required=False,
            scraper_repaired=True,
            recovery_verified=False,
            reasons=["post_repair_validation_failed"],
            steps=["Repair failed validation."],
        )

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "recovery.json"

            with patch(
                "sys.argv",
                [
                    "nexwatch",
                    "recover",
                    "--collector-id",
                    "c_test",
                    "--url",
                    "https://news.ycombinator.com",
                    "--current",
                    str(DEGRADED),
                    "--baseline",
                    str(BASELINE),
                    "--output",
                    str(output_path),
                ],
            ):
                result = main()

            self.assertEqual(result, 1)

            report = json.loads(
                output_path.read_text(encoding="utf-8")
            )

            self.assertEqual(
                report["status"],
                "verification_failed",
            )
            self.assertFalse(
                report["recovery_verified"]
            )


if __name__ == "__main__":
    unittest.main()
