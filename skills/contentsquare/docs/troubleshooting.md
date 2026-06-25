# Troubleshooting

Start here when Contentsquare auth does not connect, a read returns the wrong shape, or the agent says it is blocked.

Most setup failures mean one of three things is missing: local OAuth credentials, the right project id for account-level credentials, or Contentsquare entitlement for the API family you asked to use. Nothing changed in Contentsquare when auth setup fails.

A good first troubleshooting ask is: "Read the exact JSON error output, explain the likely missing setting, scope, entitlement, or project id in normal words, and tell me the safest next check without inventing missing data." If the target project, endpoint, integration id, date range, or permission is unclear, stop before retrying a write or broader read.

## Common checks

Start with the exact error, the token scope, the API endpoint, the project id, and the command family. Check those facts before changing credentials, widening access, or retrying a larger read.

## Missing client id or secret

Run `contentsquare-safe-cli onboarding`, then fill `.env` with the OAuth values from the Contentsquare console.

## Wrong API endpoint

Leave `CONTENTSQUARE_API_BASE_URL` empty unless Contentsquare gave you a fixed endpoint. The OAuth token response may provide the right endpoint automatically.

## Scope or permission errors

Check that the OAuth credential has access to the API family you are calling. Enrichment uses the `enrichment` scope and requires an integration id.

## Write command refused

That is usually the safe behavior. Create a dry-run plan first, review it, then apply with the saved plan and required acknowledgement flags.

## Error output

In JSON mode, the CLI prints one structured error object. Use that exact JSON error output as the first clue, but do not paste secrets, tokens, or full exported data into chat.

Use `--verbose` only when you need request start and end lines. Use `--debug` only when debugging the code itself, because it can print a Python stack trace.

## Proof limits

Local tests and `auth check` can prove that the tool and OAuth path work on the machine. They do not prove live Contentsquare account behavior for every API family. Treat live behavior as unverified until a real safe-target read succeeds with the intended account, project, scope, and entitlement.
