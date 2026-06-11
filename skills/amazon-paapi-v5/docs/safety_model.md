# Safety model

Rules:
- Amazon API calls are read-only.
- Refuse when unsure; do not guess.
- Batch jobs stop on first error and emit exactly one JSON summary object.
- Never log secrets.
