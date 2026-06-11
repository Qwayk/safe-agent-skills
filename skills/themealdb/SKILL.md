---
name: themealdb-safe-reader
description: Use the qwayk TheMealDB safe CLI for read-only free V1 meal discovery tasks. Good for categories, meal lookup, search, area filters, ingredient filters, and random meal ideas. Do not use for premium V2, uploads, or generic raw API calls.
---

# TheMealDB Safe Reader

This page is the agent-facing rule sheet for the public TheMealDB skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.

Use this skill when you need read-only meal data from the official TheMealDB free V1 public API.

## Rules

- Use `qwayk-themealdb-safe-agent-cli` only.
- Use named commands only.
- Keep `--output json`.
- Default to the built-in public key `1`.
- Do not ask for secrets unless the user explicitly wants to use a custom key.
- Refuse premium V2, upload requests, and raw passthrough requests.

## Setup

If setup is unclear, run:

```bash
qwayk-themealdb-safe-agent-cli --output json onboarding
qwayk-themealdb-safe-agent-cli --output json auth check
```

## Command map

- Categories with details:

```bash
qwayk-themealdb-safe-agent-cli --output json categories
```

- Category names only:

```bash
qwayk-themealdb-safe-agent-cli --output json list categories
```

- Areas:

```bash
qwayk-themealdb-safe-agent-cli --output json list areas
```

- Ingredients:

```bash
qwayk-themealdb-safe-agent-cli --output json list ingredients
```

- Search by meal name:

```bash
qwayk-themealdb-safe-agent-cli --output json search name --name "Arrabiata"
```

- Search by first letter:

```bash
qwayk-themealdb-safe-agent-cli --output json search first-letter --letter a
```

- Lookup one meal:

```bash
qwayk-themealdb-safe-agent-cli --output json lookup id --meal-id 52772
```

- Random meal:

```bash
qwayk-themealdb-safe-agent-cli --output json random
```

- Filter by ingredient:

```bash
qwayk-themealdb-safe-agent-cli --output json filter ingredient --ingredient chicken_breast
```

- Filter by category:

```bash
qwayk-themealdb-safe-agent-cli --output json filter category --category Seafood
```

- Filter by area:

```bash
qwayk-themealdb-safe-agent-cli --output json filter area --area Canadian
```

## Notes

- `list ingredients` is large because the API returns long ingredient records.
- For empty search or filter results, treat the empty array as a normal no-match result.
