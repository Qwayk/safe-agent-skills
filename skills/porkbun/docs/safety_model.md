# Review changes and keep keys private

## Before you apply a change

Save a plan and check the account, the exact target, what will change, the current state and any cost. Check how the tool will verify the result. After the user approves, apply the same command and input with `--plan-in`, `--apply`, `--yes` and the flags the plan calls for.

- `--ack-spend` for registration, renewal and transfer.
- `--ack-terms` for registration. Include `agreeToTerms` in the JSON input with `"yes"` or `"1"`.
- `--ack-destructive` for deletions.
- `--ack-secret` for secret-bearing reads and writes, and for email password changes.
- `--ack-send` for account invites, webhook tests and webhook resends.
- `--ack-no-snapshot` when the command allows a change without a reliable record of the current state. Confirm that risk before using the flag.

The tool signs the saved plan with HMAC-SHA256 using `.state/plan-signing.key`. It checks the signature, account keys, target, inputs, expiry and approval flags before applying. Keep the same working directory and key pair for both commands. If the signature fails, the keys change, or the plan predates the account check, save a new plan for review. When several processes create their first plan together, they share one private 32-byte signing key.

For DNS edits and deletes by ID or by name and type, the tool reads the affected records again before applying. If it cannot confirm the reviewed records or sees a change, it stops. `--ack-no-snapshot` cannot skip this check. For a purchase, the tool asks Porkbun for a fresh preview. It proceeds only if the price matches the one you reviewed and Porkbun returns `dryRun: true` and `wouldSucceed: true`.

## After you apply

Read the receipt and check the target, what the provider said changed, and the verification result. For DNS edits and deletes, the tool checks whether Porkbun returns the expected records or confirms the deleted records are gone. This checks Porkbun's records. DNS caches update on their own schedule.

For other operations, the receipt may show the provider response or the result of a follow-up read. If `verification.confirmed` is false, check the current state before claiming success or repeating the change. Use the receipt and the current state to plan any correction.

## Keep local files private

For a secret-bearing result, use `--ack-secret --secret-out ./secrets/result.json`. The tool checks and reserves the file before it contacts Porkbun. Pick a writable file path that is safe to use. Directories and symbolic links are refused. It saves the full result there and removes secrets from normal output, error messages, plans and receipts.

Choose a different path for each plan, receipt and secret output. Keep those paths separate from the env, JSON input and plan input files. The tool checks for paths that point to the same file, including through `..`, links or other names.

Tool-created `.state` directories use `0700`. The signing key, saved plans, receipts, onboarding env files and secret results use `0600`. The tool saves these files in one step so a partial write is never treated as complete.

Porkbun requests use the two hosts listed in [Onboarding](onboarding.md). A redirect response (`HTTP_REDIRECT`) stops the command before it can send the keys to another address.
