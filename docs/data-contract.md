# NexWatch Data Contract

## Initial Regulatory News Record

```json
{
  "title": "string",
  "date": "string",
  "url": "string",
  "summary": "string"
}

Requirements

Every extracted record should:

contain a non-empty title
contain a valid source URL
contain a recognizable publication date where available
contain a useful summary where available
Health Signals

For each extraction run NexWatch should eventually calculate:

total records
records with missing fields
field completeness
duplicate rate
schema conformity
extraction success rate
Future Fields

Potential future metadata:

source
category
extraction timestamp
content hash
confidence
change type
healing status