# instagram-api-tool

Safe CLI for the official Meta Instagram API with Instagram Login.

This tool is for Instagram professional accounts with the Instagram Login product choice. Facebook-Login-only areas such as Business Discovery, Hashtag Search, and Threads account edges are tracked in `docs/api_coverage.md` as excluded by product choice.

Read commands can run normally when auth is configured. Current write commands create reviewable plans, and live apply needs explicit no-snapshot approval before Instagram HTTP, local token-file writes, or receipt output when command-specific saved snapshot support is not available.

## For non-technical users: Start here (no coding)

Start with:

- Use cases (ideas + benefits): `docs/use_cases.md`
- Onboarding (setup + what to ask your agent): `docs/onboarding.md`
- Safety model (how we prevent mistakes): `docs/safety_model.md`
- Skills wrappers (required for customer-ready tools): `docs/skills_wrappers.md`

## For technical users: Start here (CLI)

Full references:
- `docs/quickstart.md`
- `docs/command_reference.md`

Minimal examples:

```bash
instagram-api-tool --version
instagram-api-tool onboarding
instagram-api-tool auth check
```

## Proof pack (customer-ready)

- `docs/proof.md`
- `docs/api_coverage.md`
- `docs/examples/`
