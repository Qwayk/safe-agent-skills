# GiantPanda commands

Put global flags before the command. Use `--env-file <path>` to choose a settings file (default `.env`), `--output json` or `--output text` to choose the format (default `json`), or `--verbose` to see request details with the token hidden. Run `giantpanda --version` to show the installed version. Use `giantpanda --output text --help` for command-line help.

## Set up and check access

```bash
giantpanda onboarding
giantpanda auth check
```

For a different settings file, use the same `--env-file` for both commands. [Setup guide](onboarding.md)

## Read stats

```bash
giantpanda domains stats --start-date YYYY-MM-DD --end-date YYYY-MM-DD
giantpanda domains stats --start-date YYYY-MM-DD --end-date YYYY-MM-DD --page 2 --page-size 50
```

Both dates are required and the start date must be on or before the end date. Page and page size are optional positive integers. Read the paging information in the reply to find the remaining pages.

## Add domains

```bash
giantpanda domains add --domain example.com --plan-out approved-domains.json
giantpanda domains add --apply --plan-in approved-domains.json \
  --approve-plan <plan_id> --ack-no-snapshot --domain example.com
```

Repeat `--domain` for every name. You can provide up to 100 names per command. The tool puts names in lowercase and removes duplicates. Use domain names such as `example.com`, without URLs, ports, spaces, or wildcards. For a domain written in another alphabet, use its ASCII form, such as a name beginning with `xn--`.

`--dry-run` explicitly selects the default local plan. `--plan-out` is optional. Use the saved plan file, its ID, and the same domain list when you apply. Use `--receipt-out <path>` to save an extra copy in a new file. [Review the plan and the result](safety_model.md)
