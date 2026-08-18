import unittest

from src.nexwatch.validator import validate_hacker_news


def make_record(
    title="Test Story",
    url="https://example.com/story",
    points=10,
    author="tester",
    comment_count=5,
):
    return {
        "title": title,
        "url": url,
        "points": points,
        "author": author,
        "comment_count": comment_count,
    }


class ValidatorTests(unittest.TestCase):

    def setUp(self):
        self.baseline = [
            make_record(title=f"Story {i}", url=f"https://example.com/{i}")
            for i in range(30)
        ]

    def test_healthy_extraction(self):
        current = [
            make_record(title=f"Story {i}", url=f"https://example.com/{i}")
            for i in range(30)
        ]

        report = validate_hacker_news(
            current_records=current,
            baseline_records=self.baseline,
        )

        self.assertEqual(report.status, "healthy")
        self.assertEqual(report.total_records, 30)
        self.assertEqual(report.baseline_records, 30)
        self.assertEqual(report.invalid_url_count, 0)
        self.assertEqual(report.duplicate_count, 0)
        self.assertEqual(report.critical_issues, [])

    def test_optional_field_missing_creates_warning(self):
        current = [
            make_record(title=f"Story {i}", url=f"https://example.com/{i}")
            for i in range(30)
        ]

        del current[0]["comment_count"]

        report = validate_hacker_news(
            current_records=current,
            baseline_records=self.baseline,
        )

        self.assertEqual(report.status, "warning")
        self.assertEqual(report.invalid_url_count, 0)
        self.assertEqual(report.critical_issues, [])
        self.assertTrue(
            any("comment_count" in warning for warning in report.warnings)
        )

    def test_invalid_required_url_creates_critical_issue(self):
        current = [
            make_record(title=f"Story {i}", url=f"https://example.com/{i}")
            for i in range(30)
        ]

        current[0]["url"] = "not-a-valid-url"

        report = validate_hacker_news(
            current_records=current,
            baseline_records=self.baseline,
        )

        self.assertEqual(report.status, "critical")
        self.assertEqual(report.invalid_url_count, 1)
        self.assertTrue(report.critical_issues)

    def test_record_count_drop_creates_critical_issue(self):
        current = [
            make_record(title=f"Story {i}", url=f"https://example.com/{i}")
            for i in range(20)
        ]

        report = validate_hacker_news(
            current_records=current,
            baseline_records=self.baseline,
        )

        self.assertEqual(report.status, "critical")
        self.assertEqual(report.total_records, 20)
        self.assertGreater(
            report.record_count_deviation_percent,
            25.0,
        )

    def test_duplicate_records_create_warning(self):
        current = [
            make_record(title=f"Story {i}", url=f"https://example.com/{i}")
            for i in range(30)
        ]

        current[1] = current[0].copy()

        report = validate_hacker_news(
            current_records=current,
            baseline_records=self.baseline,
        )

        self.assertEqual(report.status, "warning")
        self.assertEqual(report.duplicate_count, 1)
        self.assertTrue(
            any("duplicate" in warning.lower() for warning in report.warnings)
        )


if __name__ == "__main__":
    unittest.main()