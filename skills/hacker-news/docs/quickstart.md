# Quickstart

Technical reference. If you want the simpler overview, start with `use_cases.md` and `onboarding.md`.

## Install

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

## First checks

```bash
hacker-news-api-tool --output json --version
hacker-news-api-tool --output json onboarding
hacker-news-api-tool --output json auth check
```

## First reads

```bash
hacker-news-api-tool --output json stories top
hacker-news-api-tool --output json items get --id 8863
hacker-news-api-tool --output json users get --id pg
hacker-news-api-tool --output json updates get
```
