# Bulk commands

The tool does not have a generic CSV jobs runner, shell loop, or "run this request for every row" command. Hidden fan-out is too easy to turn into duplicate contacts, unexpected cost, or a change to the wrong accounts.

Bulk work is allowed only when Twilio documents a specific bulk operation and that operation appears as a fixed command in the pinned catalog. Examples include `lookups-v2 create-bulk-lookup`, `accounts-v1 create-bulk-contacts`, and `voice-v1 create-dialing-permissions-country-bulk-update`.

## Required review

A bulk command always produces a plan first. Apply requires:

- the same command and input used to create the plan
- an exact target list derived from the validated request body
- a derived target count from 1 to 25
- `--plan-in` with that reviewed plan
- `--apply --yes`
- `--ack-bulk`
- `--target-count N`, with `N` equal to the derived list length
- every other acknowledgement named in the plan, such as spend, contact, production, or no-snapshot

The tool refuses the plan when the declared target list is missing or it cannot derive an exact count. Apply is refused when `--target-count` differs from that derived count. More than 25 targets is always refused, even if Twilio accepts a larger batch. Do not split larger work into a hidden agent loop.

## Normal contact commands stay single-target

A normal message or contact command refuses an input list with more than one recipient. Use the appropriate named Twilio bulk command if one exists. If no fixed bulk operation covers the job, report that limitation rather than turning repeated single requests into an unofficial batch system.

Bulk writes are not retried automatically. A new protected receipt is created before HTTP and records the one attempt as `succeeded`, `failed`, or `uncertain`, plus any available follow-up check.
