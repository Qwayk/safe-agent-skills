# Troubleshooting

When Pipedrive stops or returns an error, start with the boring checks first: setup, account access, target IDs, API limits, and the tool's safety gates. That usually tells you whether the problem is local configuration, provider permissions, a bad request, or a write that correctly refused to run.

Keep the JSON error output. It is the best clue for an agent reviewing deals, people, organizations, activities, products, and pipeline data, and it is safer than retrying commands blindly. For any write-related error, stop before retrying and confirm the needed approval or plan.

A good first troubleshooting ask is: "Read the Pipedrive error, explain what failed in plain English, tell me the safest next check, and do not retry any write or destructive action."

## Common checks

- Missing config
  - Error text shows required fields are missing.
  - Fix by filling `.env` and rerunning `auth check`.
- Auth check fails
  - Confirm token and domain are correct.
  - Confirm the token can call read endpoints in your Pipedrive account.
- API call errors
  - Use the `--output json` response and check `error_type` and `error`.

## Error output

The tool should always print one JSON object in JSON mode.

## Keep secrets safe

- Do not share token values.
- Use a copy of your `.env` without real tokens for support.
