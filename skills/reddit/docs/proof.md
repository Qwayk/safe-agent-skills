# Reddit test results

## November 23, 2026 offline checks

Both local copies passed 39 tests. All four [quickstart commands](quickstart.md) worked with network access disabled. The checks listed account commands, previewed a recent-posts request, and previewed a sample post. Both skill files and the local links passed their checks.

The audit used simulated Reddit replies. The source checkout could read an account and recent posts in that test. A wheel install could not start because it could not find the saved command list. Sign-in could store a rejected reply and report success, and a test code appeared in a local run log. A saved plan refused the same post on apply. A simulated reply rejecting a different change was marked successful. The retirement update keeps the files as an offline reference. [Why Reddit is retiring the API](https://developers.reddit.com/app-registration)

## June 4, 2026 record

The earlier check used a local build and the saved May 22 Reddit docs. The commands and outputs below are from that record.

### Local smoke commands

```bash
qwayk-reddit-safe-agent-cli --version
qwayk-reddit-safe-agent-cli onboarding --no-write-env
qwayk-reddit-safe-agent-cli api ops list --section account
```

### Live smoke commands listed at the time

```bash
qwayk-reddit-safe-agent-cli auth login
qwayk-reddit-safe-agent-cli --live auth exchange-code --redirect-url '<paste redirect url>'
qwayk-reddit-safe-agent-cli --live auth check
qwayk-reddit-safe-agent-cli --live api get-api-v1-me
```

### Saved examples

- [Version](examples/outputs/version.json)
- [Setup](examples/outputs/onboarding.json)
- [Account command list](examples/outputs/api_ops_account.json)
- [Local account check](examples/outputs/auth_check_config_only.json)
- [Account check without a usable token](examples/outputs/auth_check.json)
- [Sample plan](examples/plan.example.json)
- [Sample receipt](examples/receipt.example.json)

The earlier record noted that Reddit could block unapproved apps and generic User-Agents. See the [approval and recovery guide](safety_model.md) for the approval requirements and limits in those examples.
