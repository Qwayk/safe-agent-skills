# First run example

This is the smallest real flow for the public Statuspage skill.
It keeps the setup simple: install, restart if needed, and ask for one public page check.

## Install

```bash
npx skills add Qwayk/safe-agent-skills@statuspage -g -y
```

If your agent needs a restart to load new skills, restart it now.

## User request

```text
Check https://status.atlassian.com and tell me if anything is down.
```

## Example short result

```text
Page: Atlassian
Overall status: All Systems Operational
Open incidents: 0
Planned maintenance: 0
Components listed: 0
```

## Example JSON result

See:

- `atlassian-summary.json`
