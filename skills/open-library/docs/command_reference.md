# Command reference

Use this page when you need the exact Open Library command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Global flags

```bash
qwayk-open-library-safe-agent-cli [--env-file .env] [--config local-open-library.json] [--timeout-s 30] [--verbose] [--debug] [--log-file run.jsonl] [--output json|text] <command>
```

Version works without `.env`:

```bash
qwayk-open-library-safe-agent-cli --output json --version
```

## onboarding

```bash
qwayk-open-library-safe-agent-cli --output json onboarding
```

Creates `.env` from `.env.example` and prints config guidance.

## search books

```bash
qwayk-open-library-safe-agent-cli --output json search books --q <text> [--fields <fields>] [--sort <sort>] [--lang <lang>] [--limit N] [--page N] [--offset N]
```

## search authors

```bash
qwayk-open-library-safe-agent-cli --output json search authors --q <text> [--limit N] [--offset N]
```

## works get

```bash
qwayk-open-library-safe-agent-cli --output json works get <work-id>
```

## works editions list

```bash
qwayk-open-library-safe-agent-cli --output json works editions list <work-id> [--limit N] [--offset N]
```

## editions get

```bash
qwayk-open-library-safe-agent-cli --output json editions get <edition-id>
```

## isbn lookup

```bash
qwayk-open-library-safe-agent-cli --output json isbn lookup <isbn>
```

## authors get

```bash
qwayk-open-library-safe-agent-cli --output json authors get <author-id>
```

## authors works list

```bash
qwayk-open-library-safe-agent-cli --output json authors works list <author-id> [--limit N] [--offset N]
```

## subjects get (experimental)

```bash
qwayk-open-library-safe-agent-cli --output json subjects get <subject> [--details] [--ebooks] [--published-in <year-or-range>] [--limit N] [--offset N]
```
