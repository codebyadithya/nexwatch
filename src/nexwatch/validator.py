from collections import Counter
from urllib.parse import urlparse

from .models import FieldHealth, HealthReport


REQUIRED_FIELDS = (
    "title",
    "url",
    "points",
    "author",
)

OPTIONAL_FIELDS = (
    "comment_count",
)

RECORD_COUNT_WARNING_THRESHOLD = 0.10
RECORD_COUNT_CRITICAL_THRESHOLD = 0.25


def _is_present(record: dict, field: str) -> bool:
    value = record.get(field)

    if value is None:
        return False

    if isinstance(value, str) and not value.strip():
        return False

    return True


def _is_valid_url(value: object) -> bool:
    if not isinstance(value, str):
        return False

    try:
        parsed = urlparse(value)
    except ValueError:
        return False

    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _duplicate_count(records: list[dict]) -> int:
    fingerprints = [
        (
            record.get("title"),
            record.get("url"),
        )
        for record in records
    ]

    counts = Counter(fingerprints)

    return sum(count - 1 for count in counts.values() if count > 1)


def validate_hacker_news(
    current_records: list[dict],
    baseline_records: list[dict],
) -> HealthReport:

    current_count = len(current_records)
    baseline_count = len(baseline_records)

    if baseline_count == 0:
        raise ValueError("Baseline must contain at least one record.")

    deviation = abs(current_count - baseline_count) / baseline_count * 100

    fields = []

    for field_name in REQUIRED_FIELDS + OPTIONAL_FIELDS:
        present = sum(
            1
            for record in current_records
            if _is_present(record, field_name)
        )

        completeness = (
            present / current_count
            if current_count > 0
            else 0.0
        )

        fields.append(
            FieldHealth(
                name=field_name,
                total_records=current_count,
                present_records=present,
                completeness=round(completeness, 4),
                required=field_name in REQUIRED_FIELDS,
            )
        )

    invalid_urls = sum(
        1
        for record in current_records
        if not _is_valid_url(record.get("url"))
    )

    duplicate_count = _duplicate_count(current_records)

    warnings = []
    critical_issues = []

    # Record-count drift
    if deviation >= RECORD_COUNT_CRITICAL_THRESHOLD * 100:
        critical_issues.append(
            f"Record count changed by {deviation:.1f}% "
            f"(baseline={baseline_count}, current={current_count})."
        )
    elif deviation >= RECORD_COUNT_WARNING_THRESHOLD * 100:
        warnings.append(
            f"Record count changed by {deviation:.1f}% "
            f"(baseline={baseline_count}, current={current_count})."
        )

    # Required-field validation
    for field in fields:
        if not field.required:
            continue

        if field.completeness < 0.90:
            critical_issues.append(
                f"Required field '{field.name}' completeness is "
                f"{field.completeness:.1%}."
            )

    # Optional-field validation
    for field in fields:
        if field.required:
            continue

        if field.completeness < 1.0:
            warnings.append(
                f"Optional field '{field.name}' is incomplete "
                f"({field.present_records}/{field.total_records})."
            )

    if invalid_urls > 0:
        critical_issues.append(
            f"{invalid_urls} invalid source URL(s) detected."
        )

    if duplicate_count > 0:
        warnings.append(
            f"{duplicate_count} duplicate record(s) detected."
        )

    # Health score
    required_fields = [
        field
        for field in fields
        if field.required
    ]

    required_completeness = (
        sum(field.completeness for field in required_fields)
        / len(required_fields)
        if required_fields
        else 0.0
    )

    record_score = max(
        0.0,
        1.0 - (deviation / 100.0),
    )

    url_score = (
        1.0 - (invalid_urls / current_count)
        if current_count > 0
        else 0.0
    )

    duplicate_score = (
        1.0 - (duplicate_count / current_count)
        if current_count > 0
        else 0.0
    )

    health_score = (
        required_completeness * 0.50
        + record_score * 0.25
        + url_score * 0.15
        + duplicate_score * 0.10
    ) * 100

    if warnings:
        health_score -= min(5.0, len(warnings) * 2.0)

    if critical_issues:
        health_score -= min(25.0, len(critical_issues) * 10.0)

    health_score = round(
        max(0.0, min(100.0, health_score)),
        2,
    )

    if critical_issues:
        status = "critical"
    elif warnings:
        status = "warning"
    else:
        status = "healthy"

    return HealthReport(
        status=status,
        health_score=health_score,
        total_records=current_count,
        baseline_records=baseline_count,
        record_count_deviation_percent=round(deviation, 2),
        invalid_url_count=invalid_urls,
        duplicate_count=duplicate_count,
        fields=fields,
        warnings=warnings,
        critical_issues=critical_issues,
    )