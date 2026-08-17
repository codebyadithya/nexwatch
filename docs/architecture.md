# NexWatch Architecture

## Initial Architecture

```text
                Public Web
                    │
                    ▼
        Bright Data Scraper Studio
                    │
                    ▼
             Custom Collector
                    │
                    ▼
            Structured Output
                    │
                    ▼
             NexWatch Backend
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
     Health      Change      Data
     Monitor     Detector    Store
        │           │
        └─────┬─────┘
              ▼
        Healing Engine
              │
              ▼
      Bright Data Self-Heal
              │
              ▼
         Validation
              │
       ┌──────┴──────┐
       ▼             ▼
    Healthy        Review
       │
       ▼
   Intelligence
       │
       ▼
   Web Dashboard