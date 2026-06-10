# hacker-news-api-tool (read-only)

## Simplicity lock

Build and change this area in the simplest way possible.

- Use the simplest solution that solves the real need.
- Use one clear path and the fewest moving parts.
- Use the shortest clear code that solves the real problem safely.
- Remove before you add.
- Do not build optional flexibility first.
- Add extra flows only after a real repeated failure proves they are needed.
- Prove each meaningful step with real testing or real evidence.

`hacker-news-api-tool` is a small, read-only CLI for the public Hacker News Firebase API. It covers the full documented v0 HTTP read surface with explicit named commands and deterministic JSON output.

## For non-technical users: Start here (no coding)

Start with these docs:

- Use cases (ideas): `docs/use_cases.md`
- Onboarding (setup + what to ask your agent): `docs/onboarding.md`
- Safety model: `docs/safety_model.md`

What you can ask an AI agent to do (examples):

- “Show me the newest Hacker News story ids.”
- “Fetch story item 8863 and explain the fields.”
- “Get the public profile for user pg.”
- “Show me the latest changed items and profiles.”

## Scope (by design)

Supported endpoints:
- `GET /v0/item/{id}.json`
- `GET /v0/user/{id}.json`
- `GET /v0/topstories.json`
- `GET /v0/newstories.json`
- `GET /v0/beststories.json`
- `GET /v0/askstories.json`
- `GET /v0/showstories.json`
- `GET /v0/jobstories.json`
- `GET /v0/maxitem.json`
- `GET /v0/updates.json`

No authentication is required for the public Hacker News API.

## For technical users: Start here (CLI)

Full references:
- `docs/quickstart.md`
- `docs/command_reference.md`

Minimal examples:

```bash
hacker-news-api-tool --output json --version
hacker-news-api-tool --output json auth check
hacker-news-api-tool --output json stories top
hacker-news-api-tool --output json items get --id 8863
```

## Agent Skills wrapper (Codex / agent runtimes)

- Wrapper docs: `docs/skills_wrappers.md`
- Skill package: `skills/hacker-news-api-safe-cli/SKILL.md`

## Proof pack (customer-ready)

- `docs/proof.md`
- `docs/api_coverage.md`
- `docs/examples/`
