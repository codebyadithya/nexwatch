# NexWatch Engineering Guidelines

## Project

NexWatch is a self-healing web intelligence platform powered by
Bright Data Scraper Studio.

The system collects publicly available web information, transforms
it into structured data, monitors extraction health, detects
meaningful changes, and supports scraper recovery.

## Hackathon

Event: Into the Scrape-Verse
Organizer: WeMakeDevs
Technology partner: Bright Data

Primary goal:
Compete for the Web-Slinger Grand Prize by making Bright Data
Scraper Studio central to a useful, technically reliable product.

## Core Requirements

- Use a custom scraper created through Bright Data Scraper Studio.
- Do not rely solely on an existing Bright Data Scrapers Library scraper.
- Use publicly available web data only.
- Keep Bright Data central to the architecture.
- Demonstrate extraction reliability and self-healing.
- Provide real structured output.
- Do not fabricate scraping or healing results.

## Engineering Principles

1. Prefer simple architecture over unnecessary complexity.
2. Keep the system understandable to a solo developer.
3. Verify APIs and CLI commands before using them.
4. Never invent Bright Data capabilities.
5. Never commit secrets or API keys.
6. Never commit `.env` files containing secrets.
7. Handle errors explicitly.
8. Avoid silently swallowing failures.
9. Validate repaired extraction before considering it healthy.
10. Add tests for reliability-critical functionality.
11. Keep scraping, validation, intelligence, and presentation
    logically separated.
12. Avoid unnecessary dependencies.

## AI-Assisted Development

AI coding assistants are allowed and will be disclosed in the
hackathon submission.

AI-generated code must be reviewed, tested, understood, and verified
by the participant.

Do not generate large speculative implementations.

Implement incrementally.

Before changing existing code:
- inspect the relevant implementation
- understand the current architecture
- identify the smallest safe change

After implementation:
- run tests
- inspect errors
- verify behavior
- document important decisions

## Data Rules

Only publicly available web data may be collected.

Do not collect:
- private information
- login-protected information
- paywalled information
- restricted information
- unnecessary personal information

## Competition Priorities

Evaluate major features against:

1. Impact
2. Creativity and innovation
3. Technical excellence
4. Use of Bright Data Scraper Studio
5. Reliability and self-healing
6. Presentation

Avoid features that add complexity without improving these areas.