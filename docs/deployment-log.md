# Deployment Log — NexWatch

This document records deployment, runtime, infrastructure, and
environment configuration decisions made during the Into the
Scrape-Verse hackathon.

---

## Project

**Name:** NexWatch  
**Repository:** `codebyadithya/nexwatch`  
**Hackathon:** Into the Scrape-Verse — WeMakeDevs × Bright Data  
**Build period:** August 17–23, 2026

---

## Deployment Philosophy

NexWatch is being developed as a small, reproducible web-intelligence
platform.

The initial implementation prioritizes:

- local development
- reproducible configuration
- environment-variable based secrets
- Bright Data Scraper Studio integration
- deterministic structured output
- easy demonstration and deployment

No production deployment is claimed until the deployment has been
successfully tested.

---

## Development Environment

### Operating system

Windows

### Runtime

Node.js `v22.18.0`

### npm

npm `10.9.3`

### Git

Git `2.50.1.windows.1`

### Bright Data CLI

`0.3.4`

### Development tools

- Cursor
- VS Code
- PowerShell
- Git / GitHub

---

## Bright Data Configuration

### Account

Bright Data account configured successfully.

### Current account balance at start of Day 1

`$52.00`

### Pending charge

`$0.00`

### Initial zone usage

| Zone | Cost | Bandwidth |
|---|---:|---:|
| cli_unlocker | $0.00 | 0 B |
| cli_browser | $0.00 | 0 B |

### Scraper Studio free allocation observed

`5,000 / 5,000`

Secrets and API credentials must never be committed to the
repository.

---

## First Successful Scraper

### Source

Hacker News

`https://news.ycombinator.com`

### Bright Data collector

`c_msx9cuzd2g7k9mklgg`

### Creation method

Bright Data Scraper Studio → Create with AI

### Status

Active scraper

### Data structure

```text
stories[]
├── title
├── url
├── points
├── author
└── comment_count