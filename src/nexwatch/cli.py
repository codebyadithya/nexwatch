import argparse
import json
from pathlib import Path

from .models import RecoveryEvidence
from .orchestrator import build_healing_prompt, evaluate_extraction
from .recovery import approve_and_verify_repair, repair_extraction


def _write_json(data, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def validate_command(args):
    report, decision, plan = evaluate_extraction(
        current_path=Path(args.current),
        baseline_path=Path(args.baseline),
    )

    result = {
        "report": report.to_dict(),
        "decision": decision.to_dict(),
        "plan": plan.to_dict(),
    }

    output = json.dumps(
        result,
        indent=2,
        ensure_ascii=False,
    )

    print(output)

    if args.output:
        _write_json(result, Path(args.output))

    return 0


def recover_command(args):
    if args.dry_run:
        report, decision, plan = evaluate_extraction(
            current_path=Path(args.current),
            baseline_path=Path(args.baseline),
        )

        healing_prompt = (
            build_healing_prompt(report)
            if decision.action == "heal"
            else None
        )

        evidence = RecoveryEvidence(
            collector_id=args.collector_id,
            target_url=args.url,
            initial_report=report.to_dict(),
            decision=decision.to_dict(),
            healing_attempted=False,
            approval_required=False,
            scraper_repaired=False,
            recovery_verified=False,
            final_report=None,
            status="dry_run",
            reasons=decision.reasons.copy(),
            steps=plan.steps.copy(),
        )

        result = {
            "status": "dry_run",
            "initial_report": report.to_dict(),
            "decision": decision.to_dict(),
            "plan": plan.to_dict(),
            "healing_prompt": healing_prompt,
            "external_action_executed": False,
            "evidence": evidence.to_dict(),
        }

        output = json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )

        print(output)

        if args.output:
            _write_json(result, Path(args.output))

        return 0

    result = repair_extraction(
        collector_id=args.collector_id,
        current_path=Path(args.current),
        baseline_path=Path(args.baseline),
        healed_output_path=Path(args.repaired_output),
        heal_output_path=Path(args.heal_output),
        approve_output_path=Path(args.approve_output),
        scraper_url=args.url,
    )

    output = json.dumps(
        result.to_dict(),
        indent=2,
        ensure_ascii=False,
    )

    print(output)

    if args.output:
        _write_json(result.to_dict(), Path(args.output))

    return 0 if result.status in {
        "healthy",
        "recovered",
        "awaiting_approval",
        "investigation_required",
    } else 1


def approve_command(args):
    recovery_report_path = Path(args.recovery_report)

    if not recovery_report_path.exists():
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": (
                        f"Recovery report not found: "
                        f"{recovery_report_path}"
                    ),
                },
                indent=2,
            )
        )
        return 1

    recovery_data = json.loads(
        recovery_report_path.read_text(encoding="utf-8")
    )

    if recovery_data.get("status") != "awaiting_approval":
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": (
                        "The recovery report is not awaiting approval."
                    ),
                    "current_status": recovery_data.get("status"),
                },
                indent=2,
            )
        )
        return 1

    result = approve_and_verify_repair(
        collector_id=args.collector_id,
        baseline_path=Path(args.baseline),
        healed_output_path=Path(args.repaired_output),
        approve_output_path=Path(args.approve_output),
        scraper_url=args.url,
        initial_health=recovery_data.get("initial_health", 0.0),
    )

    output = json.dumps(
        result.to_dict(),
        indent=2,
        ensure_ascii=False,
    )

    print(output)

    if args.output:
        _write_json(result.to_dict(), Path(args.output))

    return 0 if result.status == "recovered" else 1


def build_parser():
    parser = argparse.ArgumentParser(
        description="NexWatch extraction monitoring and recovery system"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate current extraction against a known-good baseline.",
    )

    validate_parser.add_argument(
        "--current",
        required=True,
        help="Path to current Bright Data scraper output.",
    )

    validate_parser.add_argument(
        "--baseline",
        required=True,
        help="Path to known-good baseline.",
    )

    validate_parser.add_argument(
        "--output",
        help="Optional path for the validation report JSON.",
    )

    validate_parser.set_defaults(func=validate_command)

    recover_parser = subparsers.add_parser(
        "recover",
        help="Evaluate extraction and execute the scraper recovery workflow.",
    )

    recover_parser.add_argument(
        "--collector-id",
        required=True,
        help="Bright Data collector ID.",
    )

    recover_parser.add_argument(
        "--url",
        required=True,
        help="Scraper target URL.",
    )

    recover_parser.add_argument(
        "--current",
        required=True,
        help="Path to current Bright Data scraper output.",
    )

    recover_parser.add_argument(
        "--baseline",
        required=True,
        help="Path to known-good baseline.",
    )

    recover_parser.add_argument(
        "--heal-output",
        default="data/runs/heal-result.json",
        help="Path for the Bright Data healing response.",
    )

    recover_parser.add_argument(
        "--approve-output",
        default="data/runs/approve-result.json",
        help="Path for the Bright Data approval response.",
    )

    recover_parser.add_argument(
        "--repaired-output",
        default="data/runs/repaired.json",
        help="Path for the repaired scraper output.",
    )

    recover_parser.add_argument(
        "--output",
        default="data/runs/recovery-report.json",
        help="Path for the final recovery report.",
    )

    recover_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Evaluate and plan recovery without calling Bright Data.",
    )

    recover_parser.set_defaults(func=recover_command)

    approve_parser = subparsers.add_parser(
        "approve",
        help="Approve a pending scraper repair and verify recovery.",
    )

    approve_parser.add_argument(
        "--collector-id",
        required=True,
        help="Bright Data collector ID.",
    )

    approve_parser.add_argument(
        "--url",
        required=True,
        help="Scraper target URL.",
    )

    approve_parser.add_argument(
        "--baseline",
        required=True,
        help="Path to known-good baseline.",
    )

    approve_parser.add_argument(
        "--recovery-report",
        default="data/runs/recovery-report.json",
        help="Path to the recovery report awaiting approval.",
    )

    approve_parser.add_argument(
        "--approve-output",
        default="data/runs/approve-result.json",
        help="Path for the Bright Data approval response.",
    )

    approve_parser.add_argument(
        "--repaired-output",
        default="data/runs/repaired.json",
        help="Path for the repaired scraper output.",
    )

    approve_parser.add_argument(
        "--output",
        default="data/runs/approval-recovery-report.json",
        help="Path for the final approval recovery report.",
    )

    approve_parser.set_defaults(func=approve_command)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())