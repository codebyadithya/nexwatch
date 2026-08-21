import streamlit as st


def inject_styles() -> None:
    """Inject the complete NexWatch visual system."""

    st.markdown(
        """
        <style>

        /* =========================================================
           NEXWATCH VISUAL SYSTEM
           ========================================================= */

        @import url(
            'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap'
        );

        @import url(
            'https://db.onlinewebfonts.com/c/8cb707a9b8a73f8a7403336b861c3074?family=BubbledotICG-FinePos'
        );


        :root {
            --nx-bg: #07080b;
            --nx-surface: #0d0f14;
            --nx-surface-2: #11141a;
            --nx-border: rgba(255,255,255,0.09);

            --nx-white: #f5f7fa;
            --nx-text: #e7eaf0;
            --nx-muted: #8a909d;
            --nx-dim: #5d6470;

            --nx-green: #78e6a5;
            --nx-red: #ff6b78;
            --nx-violet: #9c8cff;
            --nx-blue: #78b8ff;

            --nx-font:
                "Inter",
                "Segoe UI",
                system-ui,
                sans-serif;

            --nx-display:
                "BubbledotICG-FinePos",
                "Geist Pixel Circle",
                monospace;
        }


        /* =========================================================
           GLOBAL
           ========================================================= */

        html,
        body,
        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(
                    circle at 50% -10%,
                    rgba(120, 140, 255, 0.08),
                    transparent 35%
                ),
                var(--nx-bg) !important;

            color: var(--nx-text);
            font-family: var(--nx-font);
        }


        [data-testid="stHeader"] {
            background: transparent !important;
        }


        [data-testid="stToolbar"] {
            display: none;
        }


        .block-container {
            max-width: 1380px !important;
            padding-top: 28px !important;
            padding-bottom: 70px !important;
        }


        /* =========================================================
           REMOVE DEFAULT STREAMLIT VISUAL NOISE
           ========================================================= */

        div[data-testid="stMetric"] {
            background: transparent;
            border: none;
            padding: 0;
        }


        div[data-testid="stMetricLabel"] {
            color: var(--nx-muted) !important;
            font-size: 0.72rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }


        div[data-testid="stMetricValue"] {
            color: var(--nx-white) !important;
            font-weight: 600 !important;
        }


        div[data-testid="stMetricDelta"] {
            font-size: 0.75rem !important;
        }


        /* =========================================================
           BRAND
           ========================================================= */

        .nx-brand {
            display: flex;
            align-items: center;
            gap: 13px;
        }


        .nx-logo {
            width: 43px;
            height: 43px;

            display: flex;
            align-items: center;
            justify-content: center;

            border-radius: 50%;

            background:
                linear-gradient(
                    145deg,
                    #ffffff,
                    #dfe3ea
                );

            color: #08090b;

            font-family: var(--nx-display);
            font-size: 21px;

            box-shadow:
                0 0 0 1px rgba(255,255,255,0.16),
                0 10px 30px rgba(0,0,0,0.35);
        }


        .nx-brand-name {
            font-size: 1rem;
            font-weight: 700;
            letter-spacing: 0.16em;
        }


        .nx-brand-sub {
            margin-top: 2px;
            color: var(--nx-dim);
            font-size: 0.68rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }


        /* =========================================================
           LIVE INDICATOR
           ========================================================= */

        .nx-live {
            display: inline-flex;
            align-items: center;
            gap: 8px;

            padding: 7px 12px;

            border:
                1px solid rgba(120,230,165,0.20);

            border-radius: 999px;

            color: var(--nx-green);

            background:
                rgba(120,230,165,0.05);

            font-size: 0.68rem;
            font-weight: 600;
            letter-spacing: 0.10em;
        }


        .nx-live-dot {
            width: 6px;
            height: 6px;

            border-radius: 50%;

            background: var(--nx-green);

            box-shadow:
                0 0 0 4px rgba(120,230,165,0.08),
                0 0 12px rgba(120,230,165,0.65);

            animation: nxPulse 2s infinite;
        }


        @keyframes nxPulse {
            0%, 100% {
                opacity: 1;
                transform: scale(1);
            }

            50% {
                opacity: 0.45;
                transform: scale(0.75);
            }
        }


        /* =========================================================
           HERO
           ========================================================= */

        .nx-hero {
            margin-top: 58px;
            max-width: 900px;
        }


        .nx-eyebrow {
            color: var(--nx-violet);
            font-size: 0.68rem;
            font-weight: 600;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            margin-bottom: 12px;
        }


        .nx-headline {
            margin: 0;

            font-size: clamp(3rem, 6vw, 6.5rem);
            line-height: 0.95;

            letter-spacing: -0.065em;
            font-weight: 600;

            color: var(--nx-white);

            max-width: 900px;
        }


        .nx-headline-accent {
            color: var(--nx-muted);
        }


        .nx-description {
            max-width: 650px;

            margin-top: 22px;

            color: var(--nx-muted);

            font-size: 1rem;
            line-height: 1.7;
        }


        /* =========================================================
           SOURCE
           ========================================================= */

        .nx-source {
            margin-top: 40px;

            display: flex;
            align-items: center;
            justify-content: space-between;

            gap: 30px;

            padding: 20px 22px;

            background:
                linear-gradient(
                    135deg,
                    rgba(255,255,255,0.045),
                    rgba(255,255,255,0.018)
                );

            border: 1px solid var(--nx-border);

            border-radius: 18px;

            backdrop-filter: blur(20px);
        }


        .nx-source-label {
            color: var(--nx-dim);

            font-size: 0.66rem;
            font-weight: 600;

            letter-spacing: 0.14em;
            text-transform: uppercase;

            margin-bottom: 7px;
        }


        .nx-source-name {
            font-size: 1.05rem;
            font-weight: 600;
        }


        .nx-source-url {
            margin-top: 4px;

            color: var(--nx-muted);

            font-size: 0.78rem;
        }


        .nx-status {
            text-align: right;
        }


        .nx-status-value {
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--nx-green);
        }


        .nx-status-warning {
            color: var(--nx-red);
        }


        .nx-status-caption {
            margin-top: 5px;

            color: var(--nx-dim);

            font-size: 0.7rem;
        }


        /* =========================================================
           KPI ROW
           ========================================================= */

        .nx-kpi-grid {
            display: grid;

            grid-template-columns:
                repeat(4, minmax(0, 1fr));

            gap: 1px;

            margin-top: 26px;

            overflow: hidden;

            border:
                1px solid var(--nx-border);

            border-radius: 18px;

            background:
                var(--nx-border);
        }


        .nx-kpi {
            padding: 24px;

            background:
                rgba(13,15,20,0.94);
        }


        .nx-kpi-label {
            color: var(--nx-dim);

            font-size: 0.65rem;
            font-weight: 600;

            letter-spacing: 0.13em;
            text-transform: uppercase;
        }


        .nx-kpi-value {
            margin-top: 10px;

            color: var(--nx-white);

            font-size: 2rem;
            font-weight: 600;

            letter-spacing: -0.045em;
        }


        .nx-kpi-meta {
            margin-top: 5px;

            color: var(--nx-muted);

            font-size: 0.72rem;
        }


        /* =========================================================
           SECTION
           ========================================================= */

        .nx-section {
            margin-top: 62px;
        }


        .nx-section-header {
            display: flex;
            align-items: baseline;
            justify-content: space-between;

            margin-bottom: 18px;
        }


        .nx-section-title {
            font-size: 1rem;
            font-weight: 600;
            letter-spacing: -0.02em;
        }


        .nx-section-subtitle {
            color: var(--nx-dim);

            font-size: 0.68rem;

            letter-spacing: 0.08em;
            text-transform: uppercase;
        }


        /* =========================================================
           PIPELINE
           ========================================================= */

        .nx-pipeline {
            display: grid;

            grid-template-columns:
                repeat(6, minmax(0, 1fr));

            gap: 1px;

            background: var(--nx-border);

            border:
                1px solid var(--nx-border);

            border-radius: 18px;

            overflow: hidden;
        }


        .nx-step {
            position: relative;

            min-height: 130px;

            padding: 22px;

            background: var(--nx-surface);
        }


        .nx-step-number {
            color: var(--nx-dim);

            font-size: 0.66rem;
            font-weight: 600;

            letter-spacing: 0.12em;
        }


        .nx-step-name {
            margin-top: 31px;

            color: var(--nx-white);

            font-size: 0.9rem;
            font-weight: 600;
        }


        .nx-step-state {
            margin-top: 7px;

            color: var(--nx-green);

            font-size: 0.62rem;
            font-weight: 600;

            letter-spacing: 0.11em;
        }


        .nx-step-heal {
            color: var(--nx-violet);
        }


        /* =========================================================
           EVENT TIMELINE
           ========================================================= */

        .nx-events {
            display: flex;
            flex-direction: column;

            gap: 1px;

            background: var(--nx-border);

            border:
                1px solid var(--nx-border);

            border-radius: 18px;

            overflow: hidden;
        }


        .nx-event {
            display: grid;

            grid-template-columns: 90px 10px 1fr;

            gap: 18px;

            align-items: center;

            padding: 20px 22px;

            background: var(--nx-surface);
        }


        .nx-event-time {
            color: var(--nx-dim);

            font-size: 0.62rem;
            font-weight: 600;

            letter-spacing: 0.1em;
        }


        .nx-event-marker {
            width: 7px;
            height: 7px;

            border-radius: 50%;

            background: var(--nx-green);

            box-shadow:
                0 0 12px rgba(120,230,165,0.35);
        }


        .nx-event-marker.red {
            background: var(--nx-red);

            box-shadow:
                0 0 12px rgba(255,107,120,0.4);
        }


        .nx-event-marker.violet {
            background: var(--nx-violet);

            box-shadow:
                0 0 12px rgba(156,140,255,0.4);
        }


        .nx-event-title {
            color: var(--nx-white);

            font-size: 0.85rem;
            font-weight: 600;
        }


        .nx-event-detail {
            margin-top: 4px;

            color: var(--nx-muted);

            font-size: 0.74rem;
            line-height: 1.55;
        }


        /* =========================================================
           ISSUE LIST
           ========================================================= */

        .nx-issues {
            display: flex;
            flex-direction: column;

            gap: 8px;
        }


        .nx-issue {
            display: flex;
            align-items: flex-start;

            gap: 12px;

            padding: 13px 15px;

            background:
                rgba(255,107,120,0.045);

            border:
                1px solid rgba(255,107,120,0.10);

            border-radius: 12px;

            color: var(--nx-muted);

            font-size: 0.76rem;
            line-height: 1.5;
        }


        .nx-issue-dot {
            flex: 0 0 auto;

            margin-top: 6px;

            width: 5px;
            height: 5px;

            border-radius: 50%;

            background: var(--nx-red);
        }


        .nx-warning {
            background:
                rgba(156,140,255,0.045);

            border-color:
                rgba(156,140,255,0.10);
        }


        .nx-warning .nx-issue-dot {
            background: var(--nx-violet);
        }


        /* =========================================================
           HEALTH COMPARISON
           ========================================================= */

        .nx-health-grid {
            display: grid;

            grid-template-columns:
                repeat(2, minmax(0, 1fr));

            gap: 1px;

            background: var(--nx-border);

            border:
                1px solid var(--nx-border);

            border-radius: 18px;

            overflow: hidden;
        }


        .nx-health {
            padding: 26px;

            background: var(--nx-surface);
        }


        .nx-health-label {
            color: var(--nx-dim);

            font-size: 0.64rem;
            font-weight: 600;

            letter-spacing: 0.13em;
            text-transform: uppercase;
        }


        .nx-health-value {
            margin-top: 12px;

            color: var(--nx-white);

            font-size: 2.6rem;
            font-weight: 600;

            letter-spacing: -0.06em;
        }


        .nx-health-value span {
            color: var(--nx-muted);

            font-size: 1rem;
            margin-left: 3px;
        }


        .nx-health-bar {
            height: 4px;

            margin-top: 20px;

            overflow: hidden;

            border-radius: 999px;

            background: rgba(255,255,255,0.07);
        }


        .nx-health-fill {
            height: 100%;

            border-radius: inherit;

            background: var(--nx-green);

            box-shadow:
                0 0 15px rgba(120,230,165,0.35);
        }


        .nx-health-fill.before {
            background: var(--nx-red);

            box-shadow:
                0 0 15px rgba(255,107,120,0.3);
        }


        .nx-health-meta {
            margin-top: 9px;

            color: var(--nx-muted);

            font-size: 0.7rem;
        }


        /* =========================================================
           FOOTER
           ========================================================= */

        .nx-footer {
            margin-top: 70px;

            padding-top: 22px;

            border-top:
                1px solid var(--nx-border);

            display: flex;
            justify-content: space-between;

            color: var(--nx-dim);

            font-size: 0.65rem;

            letter-spacing: 0.08em;
            text-transform: uppercase;
        }


        /* =========================================================
           STREAMLIT DATAFRAME
           ========================================================= */

        [data-testid="stDataFrame"] {
            border:
                1px solid var(--nx-border);

            border-radius: 16px;

            overflow: hidden;
        }


        /* =========================================================
           RESPONSIVE
           ========================================================= */

        @media (max-width: 900px) {

            .nx-kpi-grid {
                grid-template-columns:
                    repeat(2, minmax(0, 1fr));
            }

            .nx-pipeline {
                grid-template-columns:
                    repeat(3, minmax(0, 1fr));
            }

            .nx-source {
                flex-direction: column;
                align-items: flex-start;
            }

            .nx-status {
                text-align: left;
            }
        }


        @media (max-width: 650px) {

            .block-container {
                padding-left: 18px !important;
                padding-right: 18px !important;
            }

            .nx-hero {
                margin-top: 35px;
            }

            .nx-headline {
                font-size: 3rem;
            }

            .nx-kpi-grid {
                grid-template-columns: 1fr;
            }

            .nx-pipeline {
                grid-template-columns:
                    repeat(2, minmax(0, 1fr));
            }

            .nx-health-grid {
                grid-template-columns: 1fr;
            }

            .nx-event {
                grid-template-columns: 70px 8px 1fr;
                gap: 12px;
            }

            .nx-footer {
                flex-direction: column;
                gap: 8px;
            }
        }

        </style>
        """,
        unsafe_allow_html=True,
    )