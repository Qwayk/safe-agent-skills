# Quickstart

This is a technical reference with commands. If you do not want commands, start with [use_cases.md](use_cases.md) and [onboarding.md](onboarding.md).

## Install

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

These examples assume the venv is active. If it is not, prefix each tool command with `.venv/bin/`.

## First run

```bash
qwayk-themealdb-safe-agent-cli onboarding
qwayk-themealdb-safe-agent-cli auth check
```

## Basic reads

```bash
qwayk-themealdb-safe-agent-cli categories
qwayk-themealdb-safe-agent-cli list categories
qwayk-themealdb-safe-agent-cli search name --name "Arrabiata"
qwayk-themealdb-safe-agent-cli search first-letter --letter a
qwayk-themealdb-safe-agent-cli lookup id --meal-id 52772
qwayk-themealdb-safe-agent-cli random
qwayk-themealdb-safe-agent-cli filter ingredient --ingredient chicken_breast
qwayk-themealdb-safe-agent-cli filter category --category Seafood
qwayk-themealdb-safe-agent-cli filter area --area Canadian
```

## JSON mode

`--output json` is the default. Every command prints exactly one JSON object to stdout.

```bash
qwayk-themealdb-safe-agent-cli --output json categories
```

## Blessed validation command

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest -q
```
