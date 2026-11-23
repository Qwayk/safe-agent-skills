# How the tool handles account information and requests

## Review the catalog request

Catalog searches and lookups preview the request by default. Review the marketplace, tracking tag, item IDs or search terms, and the information the command will ask Amazon to return. Add `--apply` after approval to send the read. With `--plan-in`, the tool checks that the current account, endpoint, and request match the saved preview. Save a new preview when any of those change or when an older preview has no account check.

Amazon can return products and errors in the same reply. A partial result shows both. An error-only reply never counts as a successful search. A receipt records the request and whether it completed. An empty search that completed successfully is different from a failed request.

## Keep account details private

`onboarding --apply` can create a private settings file and leaves an existing settings file in place. `auth token fetch --apply` can contact Amazon's sign-in endpoint and save a token for the selected account. A new token replaces the previous one only after the reply passes validation. `auth token set` remains a preview-only command.

Keep settings, tokens, and any saved account data out of chat and Git. You can use `--no-artifacts` to skip the default run files. Optional files you request with `--plan-out` or `--receipt-out` can still be saved. See [the command guide](command_reference.md).
