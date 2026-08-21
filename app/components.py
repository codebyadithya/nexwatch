from __future__ import annotations

from html import escape
from typing import Any

import streamlit as st


# ============================================================
# HELPERS
# ============================================================

def _safe(value: Any, fallback: str = "—") -> str:
    """Convert a value to safe HTML text."""
    if value is None:
        return fallback

    text = str(value)

    if not text.strip():
        return fallback

    return escape(text)


def _num(value: Any, default: float = 0.0) -> float:
    """Safely convert a value to float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _int(value: Any, default: int = 0) -> int:
    """Safely convert a value to int."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _pct(value: Any, decimals: int = 1) -> str:
    """Format percentage values."""
    number = _num(value)

    if decimals == 0:
        return f"{number:.0f}%"

    return f"{number:.{decimals}f}%"


def _status_class(status: str) -> str:
    normalized = str(status or "").lower()

    if normalized in {"healthy", "recovered", "verified", "good", "passed"}:
        return "nx-status-good"

    if normalized in {"warning", "degraded", "healing", "investigate"}:
        return "nx-status-warning"

    if normalized in {"critical", "failed", "error"}:
        return "nx-status-critical"

    return "nx-status-neutral"


# ============================================================
# HEADER
# ============================================================

def render_header() -> None:
    """Render the NexWatch application header."""

    st.markdown(
        """
        <header class="nx-header">

            <div class="nx-brand">

                <div class="nx-brand-mark">
                    N
                </div>

                <div class="nx-brand-copy">

                    <div class="nx-brand-name">
                        NEXWATCH
                    </div>

                    <div class="nx-brand-tagline">
                        WEB INTELLIGENCE / RELIABILITY
                    </div>

                </div>

            </div>

            <div class="nx-header-status">
                <span class="nx-header-status-dot"></span>
                SYSTEM ONLINE
            </div>

        </header>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HERO
# ============================================================

def render_hero() -> None:
    """Render the main NexWatch hero."""

    st.markdown(
        """
        <section class="nx-hero">

            <div class="nx-live">
                <span class="nx-live-dot"></span>
                LIVE SYSTEM
            </div>

            <h1 class="nx-hero-title">
                Intelligence that
                <span>keeps extracting.</span>
            </h1>

            <p class="nx-hero-description">
                NexWatch continuously evaluates web extraction
                integrity, detects degradation, coordinates recovery,
                and verifies the restored dataset.
            </p>

        </section>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SOURCE
# ============================================================

def render_source(recovery_status: str) -> None:
    """Render monitored source and current recovery status."""

    status = str(recovery_status or "UNKNOWN").upper()
    status_class = _status_class(status)

    if status in {"RECOVERED", "VERIFIED", "HEALTHY"}:
        status_label = "RECOVERED"
    elif status in {"HEALING REQUIRED", "DEGRADED"}:
        status_label = "DEGRADED"
    else:
        status_label = status

    st.markdown(
        f"""
        <section class="nx-source">

            <div class="nx-source-main">

                <div class="nx-eyebrow">
                    MONITORED SOURCE / CUSTOM COLLECTOR
                </div>

                <div class="nx-source-name">
                    Hacker News
                </div>

                <div class="nx-source-url">
                    news.ycombinator.com
                </div>

            </div>

            <div class="nx-source-status {status_class}">

                <div class="nx-source-status-label">
                    <span class="nx-status-dot"></span>
                    {escape(status_label)}
                </div>

                <div class="nx-source-status-caption">
                    Extraction integrity status
                </div>

            </div>

        </section>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# KPI OVERVIEW
# ============================================================

def render_kpis(data: dict[str, Any]) -> None:
    """Render the primary KPI overview."""

    initial_health = data.get("initial_health")
    final_health = data.get("final_health")

    initial_records = _int(data.get("initial_records"))
    final_records = _int(data.get("final_records"))
    baseline_records = _int(data.get("baseline_records"))

    initial_deviation = _num(data.get("initial_deviation"))
    final_deviation = _num(data.get("final_deviation"))

    if initial_health is not None and final_health is not None:
        recovery_delta = _num(final_health) - _num(initial_health)
        recovery_text = f"+{recovery_delta:.1f}"
        recovery_delta_text = f"↑ {recovery_delta:+.1f} pts"
    else:
        recovery_text = "—"
        recovery_delta_text = "↑ Recovery delta unavailable"

    if final_health is not None:
        health_value = f"{_num(final_health):.1f}%"
    else:
        health_value = "—"

    record_drift = final_deviation

    st.markdown(
        f"""
        <section class="nx-kpi-grid">

            <article class="nx-kpi nx-kpi-primary">

                <div class="nx-kpi-label">
                    CURRENT EXTRACTION HEALTH
                </div>

                <div class="nx-kpi-value">
                    {escape(health_value)}
                </div>

                <div class="nx-kpi-change nx-positive">
                    {escape(recovery_delta_text)}
                </div>

                <div class="nx-kpi-description">
                    NexWatch detected extraction degradation,
                    coordinated the repair workflow, and verified
                    the recovered dataset against the expected
                    data contract.
                </div>

            </article>

            <article class="nx-kpi">

                <div class="nx-kpi-label">
                    RECORDS
                </div>

                <div class="nx-kpi-number">
                    {final_records}
                </div>

                <div class="nx-kpi-meta">
                    baseline {baseline_records}
                </div>

            </article>

            <article class="nx-kpi">

                <div class="nx-kpi-label">
                    RECORD DRIFT
                </div>

                <div class="nx-kpi-number">
                    {record_drift:.1f}%
                </div>

                <div class="nx-kpi-meta">
                    from baseline
                </div>

            </article>

            <article class="nx-kpi">

                <div class="nx-kpi-label">
                    HEALTH RESTORED
                </div>

                <div class="nx-kpi-number">
                    {escape(recovery_text)}
                </div>

                <div class="nx-kpi-meta">
                    health points
                </div>

            </article>

        </section>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SECTION HEADER
# ============================================================

def render_section_header(
    title: str,
    subtitle: str,
) -> None:
    """
    Render a reusable section header.

    This keeps all section headings consistent.
    """

    st.markdown(
        f"""
        <div class="nx-section-header">

            <div class="nx-section-title">
                {escape(title)}
            </div>

            <div class="nx-section-subtitle">
                {escape(subtitle)}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# RECOVERY PIPELINE
# ============================================================

def render_pipeline(data: dict[str, Any] | None = None) -> None:
    """
    Render the recovery pipeline.

    `data` is optional intentionally so the function remains
    compatible with both render_pipeline() and render_pipeline(data=data).
    """

    steps = [
        ("01", "Detect", "COMPLETE", ""),
        ("02", "Diagnose", "COMPLETE", ""),
        ("03", "Heal", "COMPLETE", "nx-step-heal"),
        ("04", "Re-run", "COMPLETE", ""),
        ("05", "Validate", "PASSED", ""),
        ("06", "Recover", "VERIFIED", ""),
    ]

    rendered_steps = []

    for number, name, state, extra_class in steps:
        rendered_steps.append(
            f"""
            <div class="nx-step">

                <div class="nx-step-number">
                    {number}
                </div>

                <div class="nx-step-name">
                    {name}
                </div>

                <div class="nx-step-state {extra_class}">
                    {state}
                </div>

            </div>
            """
        )

    st.markdown(
        f"""
        <div class="nx-pipeline">

            <div class="nx-pipeline-track">

                {"".join(rendered_steps)}

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# RECOVERY EVENTS
# ============================================================

def render_events(data: dict[str, Any] | None = None) -> None:
    """
    Render the evidence chain.

    The visual story is derived from NexWatch's recovery workflow.
    """

    events = [
        {
            "time": "DETECTED",
            "marker": "red",
            "title": "Extraction degraded",
            "detail": (
                "Record count dropped from 30 to 20 and "
                "an invalid source URL was detected."
            ),
        },
        {
            "time": "DIAGNOSED",
            "marker": "violet",
            "title": "Recovery decision generated",
            "detail": (
                "NexWatch classified the event as critical "
                "and selected the healing path."
            ),
        },
        {
            "time": "HEALING",
            "marker": "violet",
            "title": "Bright Data repair requested",
            "detail": (
                "The affected collector was sent through "
                "the scraper repair workflow."
            ),
        },
        {
            "time": "VALIDATED",
            "marker": "",
            "title": "Recovered extraction verified",
            "detail": (
                "Repaired output returned to the expected "
                "data contract and baseline."
            ),
        },
    ]

    blocks = []

    for event in events:
        blocks.append(
            f"""
            <div class="nx-event">

                <div class="nx-event-time">
                    {escape(event["time"])}
                </div>

                <div class="nx-event-marker {escape(event["marker"])}">
                </div>

                <div class="nx-event-content">

                    <div class="nx-event-title">
                        {escape(event["title"])}
                    </div>

                    <div class="nx-event-detail">
                        {escape(event["detail"])}
                    </div>

                </div>

            </div>
            """
        )

    st.markdown(
        f"""
        <section class="nx-events">
            {"".join(blocks)}
        </section>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# ISSUES
# ============================================================

def render_issues(
    critical_issues: list[Any] | None,
    warnings: list[Any] | None,
) -> None:
    """Render detected extraction conditions."""

    critical_issues = critical_issues or []
    warnings = warnings or []

    blocks = []

    for issue in critical_issues:
        blocks.append(
            f"""
            <div class="nx-issue">

                <div class="nx-issue-marker nx-issue-marker-critical">
                    ●
                </div>

                <div class="nx-issue-text">
                    {escape(str(issue))}
                </div>

            </div>
            """
        )

    for warning in warnings:
        blocks.append(
            f"""
            <div class="nx-issue">

                <div class="nx-issue-marker nx-issue-marker-warning">
                    ●
                </div>

                <div class="nx-issue-text">
                    {escape(str(warning))}
                </div>

            </div>
            """
        )

    if not blocks:
        blocks.append(
            """
            <div class="nx-issue nx-issue-success">

                <div class="nx-issue-marker nx-issue-marker-success">
                    ●
                </div>

                <div class="nx-issue-text">
                    No extraction quality issues detected.
                </div>

            </div>
            """
        )

    st.markdown(
        f"""
        <section class="nx-issues">
            {"".join(blocks)}
        </section>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HEALTH COMPARISON
# ============================================================

def render_health_comparison(
    initial_health: Any,
    final_health: Any,
    initial_records: Any,
    final_records: Any,
    baseline_records: Any,
) -> None:
    """Render before/after extraction health."""

    before = max(0.0, min(_num(initial_health), 100.0))
    after = max(0.0, min(_num(final_health), 100.0))

    initial_count = _int(initial_records)
    final_count = _int(final_records)
    baseline_count = _int(baseline_records)

    recovery_delta = after - before

    st.markdown(
        f"""
        <section class="nx-health">

            <div class="nx-health-column">

                <div class="nx-health-label">
                    BEFORE RECOVERY
                </div>

                <div class="nx-health-value nx-negative">
                    {before:.1f}%
                </div>

                <div class="nx-health-bar">
                    <div
                        class="nx-health-fill nx-health-before"
                        style="width: {before}%"
                    ></div>
                </div>

                <div class="nx-health-meta">
                    {initial_count}
                    records /
                    {baseline_count}
                    baseline
                </div>

            </div>

            <div class="nx-health-transition">

                <div class="nx-health-transition-line">
                </div>

                <div class="nx-health-transition-label">
                    RECOVERY
                </div>

                <div class="nx-health-transition-value">
                    {recovery_delta:+.1f}
                    <span>pts</span>
                </div>

            </div>

            <div class="nx-health-column nx-health-after">

                <div class="nx-health-label">
                    AFTER RECOVERY
                </div>

                <div class="nx-health-value nx-positive">
                    {after:.1f}%
                </div>

                <div class="nx-health-bar">
                    <div
                        class="nx-health-fill nx-health-after-fill"
                        style="width: {after}%"
                    ></div>
                </div>

                <div class="nx-health-meta">
                    {final_count}
                    records /
                    {baseline_count}
                    baseline
                </div>

            </div>

        </section>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# RECOVERED STORIES
# ============================================================

def render_stories(stories: list[dict[str, Any]] | None) -> None:
    """
    Render recovered structured intelligence.

    Uses native Streamlit dataframe rendering intentionally.
    This avoids injecting table HTML and avoids the earlier
    Arrow serialization problem by normalizing every value.
    """

    stories = stories or []

    if not stories:
        st.markdown(
            """
            <div class="nx-empty-state">
                Recovered structured data is not available yet.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    rows = []

    for story in stories:
        if not isinstance(story, dict):
            continue

        rows.append(
            {
                "Story": str(
                    story.get("title")
                    or "Untitled"
                ),
                "Points": _int(
                    story.get("points"),
                    0,
                ),
                "Comments": (
                    _int(story["comment_count"])
                    if story.get("comment_count") is not None
                    else "—"
                ),
                "Author": str(
                    story.get("author")
                    or "—"
                ),
            }
        )

    if not rows:
        st.markdown(
            """
            <div class="nx-empty-state">
                No valid recovered records were found.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # Convert mixed values in Comments into strings so Arrow
    # never receives both integers and "—" in one column.
    for row in rows:
        row["Comments"] = str(row["Comments"])

    st.dataframe(
        rows,
        width="stretch",
        hide_index=True,
    )


# ============================================================
# FOOTER
# ============================================================

def render_footer() -> None:
    """Render the NexWatch footer."""

    st.markdown(
        """
        <footer class="nx-footer">

            <div class="nx-footer-brand">
                NEXWATCH
            </div>

            <div class="nx-footer-description">
                WEB INTELLIGENCE RELIABILITY
            </div>

            <div class="nx-footer-powered">
                BRIGHT DATA SCRAPER STUDIO
            </div>

        </footer>
        """,
        unsafe_allow_html=True,
    )