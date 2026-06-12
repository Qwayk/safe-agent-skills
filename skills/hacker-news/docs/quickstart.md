# Quickstart

This is the technical command path for Hacker News. If you want the simpler overview first, start with [What you can do with Hacker News](use_cases.md), [Use Hacker News with no account](onboarding.md), and [How this skill stays safe](safety_model.md).

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
