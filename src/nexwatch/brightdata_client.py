import json
import subprocess
from pathlib import Path


class BrightDataError(RuntimeError):
    """Raised when a Bright Data CLI operation fails."""


def _run_command(command: list[str]) -> dict:
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        raise BrightDataError(
            f"Bright Data command failed ({result.returncode}): {message}"
        )

    output = result.stdout.strip()

    if not output:
        return {}

    try:
        return json.loads(output)
    except json.JSONDecodeError as exc:
        raise BrightDataError(
            "Bright Data CLI returned non-JSON output."
        ) from exc


def run_scraper(
    collector_id: str,
    url: str,
    output_path: Path,
) -> dict:
    command = [
        "brightdata.cmd",
        "scraper",
        "run",
        collector_id,
        url,
        "--json",
    ]

    result = _run_command(command)

    output_path.write_text(
        json.dumps(result, indent=2) + "\n",
        encoding="utf-8",
    )

    return result


def heal_scraper(
    collector_id: str,
    prompt: str,
    url: str,
    output_path: Path,
) -> dict:
    if len(prompt) > 1000:
        raise ValueError("Healing prompt must be 1000 characters or fewer.")

    command = [
        "brightdata.cmd",
        "scraper",
        "heal",
        collector_id,
        prompt,
        "--url",
        url,
        "--json",
    ]

    result = _run_command(command)

    output_path.write_text(
        json.dumps(result, indent=2) + "\n",
        encoding="utf-8",
    )

    return result


def approve_heal(
    collector_id: str,
    url: str,
    output_path: Path,
) -> dict:
    command = [
        "brightdata.cmd",
        "scraper",
        "approve",
        collector_id,
        "--url",
        url,
        "--json",
    ]

    result = _run_command(command)

    output_path.write_text(
        json.dumps(result, indent=2) + "\n",
        encoding="utf-8",
    )

    return result
