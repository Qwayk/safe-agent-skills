---
name: porkbun
description: Check Porkbun domains, prices, DNS, SSL and webhooks, or prepare and apply a change after the user approves it.
---

# Porkbun

Start with what the user wants to check or change. Use the 66 named `porkbun` commands and keep keys out of chat, shell arguments and results. Use the [command list](docs/command_reference.md) to find the operation.

## Connect and read

For a new setup, run:

```bash
porkbun --version
porkbun --output json --env-file porkbun.env onboarding
```

Tell the user which env file to fill in. Use that path for later commands. When you need to check the connection, run `porkbun --output json --env-file porkbun.env auth check`. Then read the data the user asked for. See [account setup](docs/onboarding.md).

## Prepare and apply a change

1. Run the change command with `--plan-out`. Check the exact account, target, current state, proposed change, cost and approval flags.
2. Show the user what will happen and ask for approval. Use `--ack-spend` for registration, renewal and transfers, and `--ack-terms` with `agreeToTerms` in the input for registration. Use any other required flags in the [approval guide](docs/safety_model.md).
3. After approval, run the same command with `--plan-in`, `--apply` and `--yes`. Use the same Porkbun keys, input files and working directory with its private `.state`.
4. Read the receipt. Say what Porkbun confirmed and what still needs checking. If keys or DNS records changed, or the fresh purchase preview failed, stop and explain what needs a new review.

For secret-bearing results, use `--ack-secret` and `--secret-out` to save the result to a private file. Keep plan, receipt and secret outputs separate from each other and any input file. For an account invite status check, put the token in a private JSON file and pass it with `--input`.

Provider requests go through the CLI to Porkbun's two official hosts. Treat redirects as errors. See [offline checks](docs/proof.md) for the evidence behind the tool.
