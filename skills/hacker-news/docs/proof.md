# Hacker News test results

## November 23, 2026 local checks

Both local copies passed 40 offline tests after a fresh wheel install. I ran the installed CLI from an empty folder. With simulated replies, it opened item `8863`, kept the order of the top stories, returned an empty story list, and gave an error for replies that did not match the request. The API address from `--api-root` took priority over the shell and settings file.

A fresh local Codex install matched all 45 files under the existing skill name, `hacker-news-api-safe-cli`. Before these changes, a live read opened item `8863` and the top list returned 500 story IDs.

## May 21, 2026 checks

The original checks used CLI version `0.1.0` and the Hacker News Firebase API v0. [See the saved replies](examples/README.md) for the version, connection check, top stories, item `8863`, user `pg`, and recent updates.

## Run the checks

Run the tests inside the tool folder.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest -q
```

The tests use simulated replies for the network calls. To check the connection yourself, run `hacker-news-api-tool --output json auth check` with the CLI installed. For exact commands and error meanings, see the [command guide](command_reference.md). For the ten HTTP reads and their tests, see [API coverage](api_coverage.md).
