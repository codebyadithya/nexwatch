import unittest

from src.nexwatch.healing import (
    build_healing_plan,
    decide_healing,
)
from src.nexwatch.models import HealthReport


def make_report(
    status="healthy",
    health_score=100.0,
    deviation=0.0,
    invalid_urls=0,
    duplicates=0,
    warnings=None,
    critical_issues=None,
):
    return HealthReport(
        status=status,
        health_score=health_score,
        total_records=30,
        baseline_records=30,
        record_count_deviation_percent=deviation,
        invalid_url_count=invalid_urls,
        duplicate_count=duplicates,
        warnings=warnings or [],
        critical_issues=critical_issues or [],
    )


class HealingDecisionTests(unittest.TestCase):

    def test_healthy_report_requires_no_action(self):
        report = make_report()

        decision = decide_healing(report)

        self.assertEqual(decision.action, "none")
        self.assertEqual(decision.severity, "healthy")
        self.assertEqual(decision.reasons, [])

    def test_warning_report_requires_investigation(self):
        report = make_report(
            status="warning",
            health_score=98.0,
            warnings=["Optional field incomplete"],
        )

        decision = decide_healing(report)

        self.assertEqual(decision.action, "investigate")
        self.assertEqual(decision.severity, "warning")

    def test_record_drift_triggers_healing(self):
        report = make_report(
            status="critical",
            health_score=70.0,
            deviation=33.33,
            critical_issues=["Record count changed"],
        )

        decision = decide_healing(report)

        self.assertEqual(decision.action, "heal")
        self.assertEqual(decision.severity, "critical")
        self.assertIn("record_count_drift", decision.reasons)

    def test_invalid_url_triggers_healing(self):
        report = make_report(
            status="critical",
            health_score=90.0,
            invalid_urls=1,
            critical_issues=["Invalid URL"],
        )

        decision = decide_healing(report)

        self.assertEqual(decision.action, "heal")
        self.assertIn("invalid_url", decision.reasons)

    def test_multiple_failures_are_preserved(self):
        report = make_report(
            status="critical",
            health_score=68.92,
            deviation=33.33,
            invalid_urls=1,
            critical_issues=[
                "Record count changed",
                "Invalid URL",
            ],
        )

        decision = decide_healing(report)

        self.assertEqual(decision.action, "heal")
        self.assertIn("record_count_drift", decision.reasons)
        self.assertIn("invalid_url", decision.reasons)

    def test_healthy_report_creates_no_action_plan(self):
        report = make_report()

        decision = decide_healing(report)
        plan = build_healing_plan(report, decision)

        self.assertEqual(plan.action, "none")
        self.assertEqual(plan.severity, "healthy")
        self.assertEqual(
            plan.steps,
            ["No healing required."],
        )

    def test_warning_report_creates_investigation_plan(self):
        report = make_report(
            status="warning",
            health_score=98.0,
            warnings=["Optional field incomplete"],
        )

        decision = decide_healing(report)
        plan = build_healing_plan(report, decision)

        self.assertEqual(plan.action, "investigate")
        self.assertEqual(plan.severity, "warning")
        self.assertIn(
            "Inspect extraction health warnings.",
            plan.steps,
        )
        self.assertNotIn(
            "Request repair of the affected Bright Data scraper.",
            plan.steps,
        )

    def test_critical_report_creates_healing_plan(self):
        report = make_report(
            status="critical",
            health_score=68.92,
            deviation=33.33,
            invalid_urls=1,
            critical_issues=[
                "Record count changed",
                "Invalid URL",
            ],
        )

        decision = decide_healing(report)
        plan = build_healing_plan(report, decision)

        self.assertEqual(plan.action, "heal")
        self.assertEqual(plan.severity, "critical")

        self.assertIn(
            "record_count_drift",
            plan.reasons,
        )
        self.assertIn(
            "invalid_url",
            plan.reasons,
        )

        self.assertIn(
            "Request repair of the affected Bright Data scraper.",
            plan.steps,
        )

        self.assertIn(
            "Re-run the repaired scraper.",
            plan.steps,
        )

        self.assertIn(
            "Declare recovery only if validation succeeds.",
            plan.steps,
        )


if __name__ == "__main__":
    unittest.main()
