import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.nexwatch.brightdata_client import (
    BrightDataError,
    approve_heal,
    heal_scraper,
    run_scraper,
)


class BrightDataClientTests(unittest.TestCase):

    @patch("src.nexwatch.brightdata_client.subprocess.run")
    def test_run_scraper_builds_expected_command(self, mock_run):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = '{"stories": []}'
        mock_run.return_value.stderr = ""

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "run.json"

            result = run_scraper(
                collector_id="c_test",
                url="https://news.ycombinator.com",
                output_path=output_path,
            )

            command = mock_run.call_args.args[0]

            self.assertEqual(
                command,
                [
                    "brightdata.cmd",
                    "scraper",
                    "run",
                    "c_test",
                    "https://news.ycombinator.com",
                    "--json",
                ],
            )

            self.assertEqual(result, {"stories": []})
            self.assertTrue(output_path.exists())

    @patch("src.nexwatch.brightdata_client.subprocess.run")
    def test_heal_scraper_builds_expected_command(self, mock_run):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = '{"status": "awaiting_approval"}'
        mock_run.return_value.stderr = ""

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "heal.json"

            result = heal_scraper(
                collector_id="c_test",
                prompt="The story URL field stopped extracting correctly.",
                url="https://news.ycombinator.com",
                output_path=output_path,
            )

            command = mock_run.call_args.args[0]

            self.assertEqual(
                command,
                [
                    "brightdata.cmd",
                    "scraper",
                    "heal",
                    "c_test",
                    "The story URL field stopped extracting correctly.",
                    "--url",
                    "https://news.ycombinator.com",
                    "--json",
                ],
            )

            self.assertEqual(
                result,
                {"status": "awaiting_approval"},
            )

    @patch("src.nexwatch.brightdata_client.subprocess.run")
    def test_approve_heal_builds_expected_command(self, mock_run):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = '{"status": "done"}'
        mock_run.return_value.stderr = ""

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "approve.json"

            result = approve_heal(
                collector_id="c_test",
                url="https://news.ycombinator.com",
                output_path=output_path,
            )

            command = mock_run.call_args.args[0]

            self.assertEqual(
                command,
                [
                    "brightdata.cmd",
                    "scraper",
                    "approve",
                    "c_test",
                    "--url",
                    "https://news.ycombinator.com",
                    "--json",
                ],
            )

            self.assertEqual(result, {"status": "done"})

    @patch("src.nexwatch.brightdata_client.subprocess.run")
    def test_failed_command_raises_error(self, mock_run):
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = "authentication failed"

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "run.json"

            with self.assertRaises(BrightDataError):
                run_scraper(
                    collector_id="c_test",
                    url="https://news.ycombinator.com",
                    output_path=output_path,
                )

    def test_healing_prompt_limit_is_enforced(self):
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "heal.json"

            with self.assertRaises(ValueError):
                heal_scraper(
                    collector_id="c_test",
                    prompt="x" * 1001,
                    url="https://news.ycombinator.com",
                    output_path=output_path,
                )



    @patch("src.nexwatch.brightdata_client.subprocess.run")
    def test_list_response_is_supported(self, mock_run):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = '[{"stories": []}]'
        mock_run.return_value.stderr = ""

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "run.json"

            result = run_scraper(
                collector_id="c_test",
                url="https://news.ycombinator.com",
                output_path=output_path,
            )

            self.assertIsInstance(result, list)
            self.assertEqual(result, [{"stories": []}])

if __name__ == "__main__":
    unittest.main()


