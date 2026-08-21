import streamlit as st

from app.components import (
    render_events,
    render_footer,
    render_header,
    render_health_comparison,
    render_hero,
    render_issues,
    render_kpis,
    render_pipeline,
    render_section_header,
    render_source,
    render_stories,
)
from app.data import build_dashboard_data
from app.style import inject_styles


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="NexWatch — Web Intelligence Reliability",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# VISUAL SYSTEM
# ============================================================

inject_styles()


# ============================================================
# LOAD NORMALIZED DASHBOARD DATA
# ============================================================

data = build_dashboard_data()


# ============================================================
# APPLICATION SHELL
# ============================================================

# Everything below is intentionally orchestration only.
# No CSS lives here.
# No data parsing lives here.
# No large HTML blocks live here.


# ============================================================
# HEADER
# ============================================================

render_header()


# ============================================================
# HERO
# ============================================================

render_hero()


# ============================================================
# MONITORED SOURCE
# ============================================================

render_source(
    recovery_status=data["recovery_status"],
)


# ============================================================
# KPI OVERVIEW
# ============================================================

render_kpis(data)


# ============================================================
# RECOVERY PIPELINE
# ============================================================

render_section_header(
    title="Recovery Pipeline",
    subtitle="Automated control loop",
)

render_pipeline(
    data=data,
)


# ============================================================
# RECOVERY INTELLIGENCE
# ============================================================

render_section_header(
    title="Recovery Intelligence",
    subtitle="Evidence chain",
)

render_events(
    data=data,
)


# ============================================================
# DETECTED CONDITIONS
# ============================================================

render_section_header(
    title="Detected Conditions",
    subtitle="Initial extraction",
)

render_issues(
    critical_issues=data["critical_issues"],
    warnings=data["warnings"],
)


# ============================================================
# EXTRACTION HEALTH
# ============================================================

render_section_header(
    title="Extraction Health",
    subtitle="Before → after recovery",
)

render_health_comparison(
    initial_health=data["initial_health"],
    final_health=data["final_health"],
    initial_records=data["initial_records"],
    final_records=data["final_records"],
    baseline_records=data["baseline_records"],
)


# ============================================================
# RECOVERED INTELLIGENCE
# ============================================================

render_section_header(
    title="Recovered Intelligence",
    subtitle="Structured output",
)

render_stories(
    stories=data["stories"],
)


# ============================================================
# FOOTER
# ============================================================

render_footer()