import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.nexwatch.orchestrator import (
    build_healing_prompt,
    evaluate_extraction,
    extract_stories,
)


class OrchestratorTests(unittest.TestCase):

    def test_extract_stories_accepts_bright_data_list_response(self):
        data = [
            {
                "stories": [
                    {
                        "title": "Example",
                        "url": "https://example.com",
                        "points": 10,
                        "author": "tester",
                    }
                ]
            }
        ]

        stories = extract_stories(data)

        self.assertEqual(len(stories), 1)
        self.assertEqual(stories[0]["title"], "Example")

    def test_extract_stories_rejects_invalid_payload(self):
        with self.assertRaises(ValueError):
            extract_stories({"stories": []})

    def test_healthy_extraction_requires_no_healing(self):
        baseline = [
            {
                "stories": [
                    {
                        "title": "Example",
                        "url": "https://example.com",
                        "points": 10,
                        "author": "tester",
                        "comment_count": 2,
                    }
                ]
            }
        ]

        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)

            baseline_path = directory / "baseline.json"
            current_path = directory / "current.json"

            baseline_path.write_text(
                json.dumps(baseline),
                encoding="utf-8",
            )

            current_path.write_text(
                json.dumps(baseline),
                encoding="utf-8",
            )

            report, decision, plan = evaluate_extraction(
                current_path=current_path,
                baseline_path=baseline_path,
            )

            self.assertEqual(report.status, "healthy")
            self.assertEqual(decision.action, "none")
            self.assertEqual(plan.action, "none")

    def test_degraded_extraction_requests_healing(self):
        baseline = [
            {
                "stories": [
                    {
                        "title": "Example",
                        "url": "https://example.com",
                        "points": 10,
                        "author": "tester",
                    }
                ]
                * 100
            }
        ]

        degraded = [
            {
                "stories": [
                    {
                        "title": "Broken",
                        "url": "not-a-url",
                        "points": 10,
                        "author": "tester",
                    }
                ]
                * 50
            }
        ]

        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)

            baseline_path = directory / "baseline.json"
            current_path = directory / "current.json"

            baseline_path.write_text(
                json.dumps(baseline),
                encoding="utf-8",
            )

            current_path.write_text(
                json.dumps(degraded),
                encoding="utf-8",
            )

            report, decision, plan = evaluate_extraction(
                current_path=current_path,
                baseline_path=baseline_path,
            )

            self.assertEqual(report.status, "critical")
            self.assertEqual(decision.action, "heal")
            self.assertEqual(plan.action, "heal")

    def test_healing_prompt_contains_detected_failure(self):
        class Report:
            record_count_deviation_percent = 33.33
            invalid_url_count = 2
            critical_issues = [
                "Required field 'url' completeness is 50.0%."
            ]

        prompt = build_healing_prompt(Report())

        self.assertIn("record count", prompt.lower())
        self.assertIn("invalid", prompt.lower())
        self.assertLessEqual(len(prompt), 1000)


if __name__ == "__main__":
    unittest.main()
