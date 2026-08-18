import argparse
import json
from pathlib import Path

from .validator import validate_hacker_news


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def extract_stories(data):
    if not isinstance(data, list) or not data:
        raise ValueError("Expected a non-empty scraper result list.")

    payload = data[0]

    if not isinstance(payload, dict):
        raise ValueError("Expected the first scraper result to be an object.")

    stories = payload.get("stories")

    if not isinstance(stories, list):
        raise ValueError("Expected scraper output to contain a stories array.")

    return stories


def main():
    parser = argparse.ArgumentParser(
        description="NexWatch extraction health validator"
    )

    parser.add_argument(
        "--current",
        required=True,
        help="Path to current Bright Data scraper output",
    )

    parser.add_argument(
        "--baseline",
        required=True,
        help="Path to known-good baseline",
    )

    parser.add_argument(
        "--output",
        help="Optional path for the health report JSON",
    )

    args = parser.parse_args()

    current_data = load_json(Path(args.current))
    baseline_data = load_json(Path(args.baseline))

    current_records = extract_stories(current_data)
    baseline_records = extract_stories(baseline_data)

    report = validate_hacker_news(
        current_records=current_records,
        baseline_records=baseline_records,
    )

    output = json.dumps(
        report.to_dict(),
        indent=2,
    )

    print(output)

    if args.output:
        Path(args.output).write_text(
            output + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()