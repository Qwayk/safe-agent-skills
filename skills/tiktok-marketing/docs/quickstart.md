# Quickstart

This is a technical reference for CLI users.
If you are not using the terminal, use the non-technical docs first:
- `use_cases.md`
- `onboarding.md`

If you want the fastest technical path:

1. Install:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

2. Create `.env` and fill the TikTok values:

```bash
tiktok-marketing-api-tool --output json onboarding
```

3. Run the live read-only auth check:

```bash
tiktok-marketing-api-tool --output json auth check
```

4. List the pinned API surface:

```bash
tiktok-marketing-api-tool --output json api ops list
```

5. Build a first read plan:

```bash
tiktok-marketing-api-tool --output json --plan-out plan.json api campaign-get --query-json query.json
```
