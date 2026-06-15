# Troubleshooting

When Awin Publisher stops or returns an error, start with the boring checks first: setup, account access, target IDs, API limits, and the tool's safety gates. That usually tells you whether the problem is local configuration, provider permissions, a bad request, or a write that correctly refused to run.

Keep the JSON error output. It is the best clue for an agent reviewing publisher accounts, advertiser programs, links, transactions, and performance data, and it is safer than retrying commands blindly. For any write-related error, stop before retrying and confirm the needed approval or plan.

A good first troubleshooting ask is: "Read the Awin Publisher error, explain what failed in plain English, tell me the safest next check, and do not retry any write or destructive action."

## Debug HTTP

- Use `--verbose` to print request and response status lines to stderr.
- Confirm `AWIN_API_TOKEN` is set and not expired.

## Debug JSON errors

- `--output json` gives structured errors without stack traces.
- Add `--debug` to print Python stack traces for unexpected runtime errors.

## Secrets

- Do not paste tokens or secret output.
- If you suspect a leaked secret, rotate immediately and update `.env`.
