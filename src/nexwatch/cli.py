import argparse
import json
from pathlib import Path

from .orchestrator import evaluate_extraction
from .recovery import repair_extraction


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

    return 0 if result.status in {"healthy", "recovered", "awaiting_approval", "investigation_required"} else 1


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

    recover_parser.set_defaults(func=recover_command)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
