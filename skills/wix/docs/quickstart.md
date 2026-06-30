# Quickstart

Start by checking which Wix account or site your local setup can see, then list a few sites before any live work is planned.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
wix-safe-agent-cli --output json auth check
wix-safe-agent-cli --output json sites query --limit 5
```

If the site list returns the account you expected, use one focused read next:

```bash
wix-safe-agent-cli --output json catalog-versioning get
wix-safe-agent-cli --output json bookings-time-slots-v2 list-event --list-event-json @list-event.json
wix-safe-agent-cli --output json bookings-reader-v2 count-extended-bookings
wix-safe-agent-cli --output json bookings-services-v2 count
wix-safe-agent-cli --output json bookings-resources-v2 count
wix-safe-agent-cli --output json bookings-resource-types-v2 count
wix-safe-agent-cli --output json bookings-staff-members count
wix-safe-agent-cli --output json calendar-schedules-v3 query --query-json '{"query":{"filter":{"appId":{"$eq":"13d21c63-b5ec-5912-8397-c3a5ddb27a97"}}}}'
wix-safe-agent-cli --output json bookings-external-calendars-v2 list-providers
wix-safe-agent-cli --output json bookings-service-options-v1 query --query-json '{"filter":{"serviceId":{"$eq":"service-id"}}}'
```

Stop there before any live change. Wix writes should move through a saved plan, review, explicit apply, and receipt.

Use these pages if you want help choosing the right first read:

- [What this skill can help you do](use_cases.md)
- [Set up your account step by step](onboarding.md)
- [See how this skill keeps changes safe](safety_model.md)

For token checks and legacy token upkeep, use:

```bash
wix-safe-agent-cli auth token create
wix-safe-agent-cli auth token refresh
wix-safe-agent-cli auth token inspect --token DUMMY-TOKEN
```

If you want exact command syntax, use [Browse the shipped command guide](command_reference.md).
