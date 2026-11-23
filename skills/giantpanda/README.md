# GiantPanda

See how much traffic your parked domains get and what they earn. Ask your agent for requests, queries, clicks, revenue, RPM, and CTR for a date range, or ask it to compare two weeks and find what changed. You can also ask it to prepare a list of domains to add to your GiantPanda account.

## Get your first report

Install the skill for your agent.

```bash
npx skills add Qwayk/safe-agent-skills@giantpanda -g -y
```

The command-line tool needs Python 3.12 or newer. From the downloaded GiantPanda folder, run `python -m pip install .` in your Python environment. Set your GiantPanda token in the [private settings file](docs/onboarding.md). Then run these commands from the folder with that file.

```bash
giantpanda --output json auth check
giantpanda --output json domains stats --start-date 2026-08-01 --end-date 2026-08-07 --page 1 --page-size 50
```

Choose the dates you need. Both dates are included. Read the remaining pages before totaling the results, and keep the dates and page size the same when you change the page number. Try asking “How much did these domains earn from August 1 to August 7? Check every page.”

## Prepare a domain add

```bash
giantpanda --output json domains add --domain example.com --domain shop.example.com
```

This saves a local plan with the exact names the tool would send. Review and approve it before running the [apply command](docs/command_reference.md#add-domains). The tool cannot undo the add. If a reply is missing or incomplete, use the saved receipt to see which names to check in the dashboard.

This tool reads stats and adds domains to GiantPanda. Domain registration, DNS, transfers, payouts, and billing are handled separately. [All guides](docs/README.md)
