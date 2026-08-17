# Baselines

This directory contains captured structured outputs from Bright Data
Scraper Studio collectors used as reference data for NexWatch reliability
and drift-detection experiments.

Baseline files are raw collector outputs and must not be manually modified.

## Current Baseline

- Source: Hacker News
- Collector: c_msx9cuzd2g7k9mklgg
- Capture date: 2026-08-17
- Records: 30
- Raw output size: 5.5 KB

## Observations

- comment_count is absent from 1 record.
- This is treated as a data-quality observation, not automatically as
  scraper failure.
- Some text contains encoding artifacts and will be evaluated separately
  by the NexWatch validation layer.
