# Quickstart

Want the short non-technical path first? Start with [What you can do with Unsplash](use_cases.md), [Connect your Unsplash access key](onboarding.md), and [How this skill stays safe](safety_model.md).

This page is for the exact commands.

One important rule first: normal research reads are straightforward, but `photos download` is the careful path because a real apply can trigger Unsplash download tracking and can write a file to your machine.

## 1) Install

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

Optional (developer tooling):

```bash
.venv/bin/python -m pip install -e '.[dev]'
```

## 2) Configure

Run onboarding or copy `.env.example` to `.env`:

```bash
unsplash-api-tool --output json onboarding
```

Then fill the Unsplash values from [Configuration](configuration.md).

## 3) First safe checks

```bash
unsplash-api-tool --output json --version
unsplash-api-tool --output json auth check
unsplash-api-tool --output json photos search --query "minimal home office" --per-page 3
unsplash-api-tool --output json stats total
```

## 4) First export

Note: `--per-page` is capped at 30, and multi-page exports require `--yes`.

```bash
unsplash-api-tool --output json --yes export photos-list --out export.json --start-page 1 --max-pages 2 --per-page 10
```

## 5) First reviewed download plan

```bash
unsplash-api-tool --output json --plan-out plan.json photos download --id PHOTO_ID --dest downloads/photo.jpg
```

## 6) Download planning rules

If you move from research into a real tracked download:

- start with the dry-run plan first
- expect `--apply` for the real download path
- expect `--yes` too if the destination file already exists and you really want overwrite
- expect explicit no-snapshot approval too when the tool cannot save useful prior state before tracking or the file write
