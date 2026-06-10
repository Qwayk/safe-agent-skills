# Open Library

This page is the agent-facing rule sheet for the public Open Library skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.

Use this skill for safe Open Library reads.

- Call only these commands:
  - `search books`
  - `search authors`
  - `works get`
  - `works editions list`
  - `editions get`
  - `isbn lookup`
  - `authors get`
  - `authors works list`
  - `subjects get`
- Do not call auth, jobs, runs, or write commands.
- Pass `--output json` and keep requests low-volume.
- Prefer explicit examples with query terms and bounded `--limit`.
