# Google Business Profile Safe CLI

This tool gives AI agents and operators a safe, explicit command surface for Google Business Profile work across accounts, locations, reviews, media, notifications, verifications, performance, place actions, lodging, and the official legacy `v4.9` methods that still matter.
It is wired for Google OAuth installed-app login and local, non-secret onboarding.
Reads can run through the explicit command families. Write commands still produce review plans, but current live write apply requires explicit no-snapshot approval before Google Business Profile HTTP until per-command before-state capture exists.

## For non-technical users: start here

- `docs/use_cases.md`
- `docs/onboarding.md`
- `docs/safety_model.md`

Plain-English example requests:

- “Show me every Google Business Profile location in this account and flag anything missing key details.”
- “Prepare a safe update for these location details, then wait for my approval before applying it.”
- “List recent reviews for this location and draft or update the owner reply safely.”
- “Complete this verification using the PIN file I saved, then prove the status changed.”
- “Show me proof for the last change, including the verification result and saved receipt.”

## For technical users: CLI references

- `docs/quickstart.md`
- `docs/command_reference.md`
- `docs/configuration.md`
- `docs/authentication.md`

## Shipped command surface

The live CLI currently includes:

- `google-business-profile-safe-cli onboarding`
- `google-business-profile-safe-cli auth login|check|token ...`
- `google-business-profile-safe-cli runs ...`
- `google-business-profile-safe-cli account-management ...`
- `google-business-profile-safe-cli business-info ...`
- `google-business-profile-safe-cli notifications accounts ...`
- `google-business-profile-safe-cli media-upload-v1 media upload`
- `google-business-profile-safe-cli business-calls locations ...`
- `google-business-profile-safe-cli place-actions ...`
- `google-business-profile-safe-cli lodging locations ...`
- `google-business-profile-safe-cli performance locations ...`
- `google-business-profile-safe-cli verifications ...`
- `google-business-profile-safe-cli legacy-v49 accounts locations reviews ...`
- `google-business-profile-safe-cli legacy-v49 accounts locations verifications ...`
- `google-business-profile-safe-cli legacy-v49 accounts locations transfer`
- `google-business-profile-safe-cli legacy-v49 accounts locations media start-upload`
- `google-business-profile-safe-cli legacy-v49 accounts locations media create`

Write commands stay dry-run by default. Apply runs use explicit safety gates such as `--apply`, `--plan-in`, `--yes`, and `--ack-irreversible` when the operation needs them. Secret-like inputs stay file-based where that is safer, such as `--pin-file`, `--verification-token-file`, and `--trusted-partner-token-file`.

## Trust and proof

- Coverage main reference: `docs/api_coverage.md`
- Machine-readable inventory: `docs/official_inventory.json`
- Local proof pack: `docs/proof.md`
- Redacted examples: `docs/examples/outputs/`

The coverage ledger stays honest about what is already shipped, what still remains in the official boundary, and any method that is gated, discontinued, or intentionally not shipping.

Current write-side slices cover `account-management`, `business-info`, `notifications`, `business-calls`, `place-actions`, `verifications`, `lodging`, `media-upload-v1`, and the legacy `v4.9` reviews, transfer, and media follow-up commands. The remaining official boundary is tracked in `docs/api_coverage.md` and `docs/official_inventory.json`.
