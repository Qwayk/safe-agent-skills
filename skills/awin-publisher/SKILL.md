---
name: awin-publisher-safe-cli
description: Check Awin publisher accounts, programs, offers, transactions, tracking links, and feeds. Prepare proof-of-purchase orders for approval.
---

# Awin Publisher

1. Use `awin-publisher-safe-cli --output json`. Pass the project’s `--env-file` when it has one. Run `auth check` and confirm the intended publisher before reading programs, transactions, reports, links, or feeds. Keep keys and private settings out of chat.
2. Use the shipped commands in the [command guide](docs/command_reference.md). For a feed, use `--out`. Use `--overwrite` only when replacing the saved copy is part of the task. If an enhanced download is unavailable, check the publisher, advertiser, and locale against Awin’s current list.
3. For proof of purchase, save a plan. Show the publisher, advertiser, order file, and duplicate check, and wait for approval. Apply with `--apply --yes --plan-in` using the same key and order file. Keep the receipt and check the orders in Awin before repeating an unclear submission.

[Setup](docs/onboarding.md) · [Approval and receipt steps](docs/safety_model.md) · [Test results](docs/proof.md)
