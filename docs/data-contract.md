# NexWatch Data Contract

## Purpose

This document defines the structured data contract used by NexWatch to
evaluate the health and reliability of web-extraction pipelines.

NexWatch separates the canonical reliability model from source-specific
scraper schemas.

The current Day-2 reference source is Hacker News.

---

## 1. Canonical Record Model

A NexWatch source adapter should normalize extracted web data into
records containing the following conceptual fields:

| Field | Type | Requirement | Description |
|---|---|---|---|
| `title` | string | Required | Primary title or name of the extracted item |
| `url` | string | Required | Public source URL |
| `date` | string | Optional | Publication or update date when available |
| `summary` | string | Optional | Short description when available |
| `source` | string | Optional | Source or publisher identifier |
| `category` | string | Optional | Source-specific category |

Required fields must be present and contain meaningful values.

Optional fields may be absent without automatically causing a critical
health failure.

---

## 2. Current Hacker News Adapter

The current Bright Data Scraper Studio collector returns:

```json
{
  "stories": [
    {
      "title": "string",
      "url": "string",
      "points": 0,
      "author": "string",
      "comment_count": 0
    }
  ],
  "input": {
    "url": "string"
  }
}
Hacker News field requirements
Field    Type    Requirement
stories    array    Required
stories[].title    string    Required
stories[].url    string    Required
stories[].points    number    Required
stories[].author    string    Required
stories[].comment_count    number    Optional
3. Baseline Observations

The initial Hacker News baseline captured on August 17, 2026 contains:

30 story records
30 titles
30 URLs
30 points values
30 authors
29 comment_count values
1 record without comment_count

Therefore comment_count is currently treated as an optional field.

The baseline itself must remain unmodified.

4. Validation Rules

NexWatch should evaluate extraction health using deterministic checks.

Critical conditions

A run should be considered critically degraded when:

the expected top-level dataset is missing
the stories array is missing
the dataset contains zero usable records
a required field is absent from a substantial portion of records
the extracted record count collapses significantly from the expected baseline
required URLs are structurally invalid
Warning conditions

A run may receive a warning when:

optional fields are missing from some records
duplicate records are detected
text contains suspicious encoding anomalies
a small number of records contain incomplete optional metadata
Healthy conditions

A run is healthy when:

the expected schema is present
required fields are substantially complete
the record count is within an acceptable range
URLs are valid
no significant structural drift is detected

Thresholds must be explicit in the validation implementation rather than
being hidden assumptions.

5. Health Signals

NexWatch should eventually calculate:

total records
required-field completeness
optional-field completeness
invalid URL count
duplicate rate
schema conformity
record-count deviation
data-quality warnings
overall health status
health score
detected drift signals
6. Baseline Comparison

A current extraction is compared against a known-good baseline.

The comparison should identify:

record-count drift
schema drift
field-completeness drift
URL validity changes
duplicate-rate changes
data-quality anomalies

The baseline is evidence, not a manually edited expected result.

7. Self-Healing Contract

NexWatch must not automatically declare a scraper recovered merely because
Bright Data reports that a scraper was healed.

Recovery requires:

detecting degradation
identifying the affected extraction
requesting scraper repair
executing the repaired scraper
validating the new output
comparing it against the expected contract
declaring recovery only when validation succeeds
8. Future Metadata

The normalized NexWatch model may later include:

extraction_timestamp
content_hash
confidence
change_type
health_status
healing_status
collector_id

These fields should only be introduced when they provide measurable value
to the reliability workflow.
