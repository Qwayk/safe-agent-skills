# What we tested

## November 23, 2026 local checks

Fresh installs from the source and local catalog each passed 128 tests with the network blocked. Both loaded the pinned 103 API3 commands and the bulk availability command. The two skill files passed validation. The lint and type checks still report existing issues. Comparing with the audit found no new warnings or errors.

Simulated replies checked a changed key, a changed receiver account, a higher quote, a renewal with the same term, and a server error during registration. The tool sent one write request for the unclear result and told the user to check the order. Tests also checked a private transfer-code export, a settings path with spaces, and refusal to follow redirects.

## November 23, 2026 coverage check

The tool keeps the 103 names in its [pinned API3 inventory](official_commands.txt). Dynadot's current docs have 107 request-example names. Five are new relative to the pinned list and one pinned name no longer appears in those examples.

- New examples are `add_new_lead`, `clear_dnssec`, `get_whois_stats`, `set_contact_lt_setting`, and `suggestion_search`.
- `set_customer_id` is still in the pinned list. It no longer appeared in the request examples we checked.

Dynadot plans to retire API3. Before expanding the tool, map the workflows people use to REST, starting with availability, domain lists, nameservers, purchases, and moves between Dynadot accounts. Check where the REST API needs a separate signing secret, and decide how people will move without losing commands they rely on. [API3 notice](https://www.dynadot.com/domain/api-commands) · [REST API docs](https://www.dynadot.com/domain/api-document)

## Earlier checks

On July 31, 2026, version `0.5.0` passed 131 offline tests, including 11 focused on availability and related reads. The live availability check returned one available name and one unavailable name. A separate live run checked 364 names in 364 sequential requests. It found 240 available and 124 unavailable, with none unresolved and no registrations. Those runs used `https://api.dynadot.com/api3.json`.

Earlier work also checked bulk pushes and accept or decline steps, nameserver exports and comparisons, readback after changes, and the guided sender-to-receiver move. The tool can plan from an earlier receipt to skip completed domains. See [redacted sample outputs](examples/outputs/) for the shapes of plans and receipts. Earlier examples may reflect an older approval flow.

## Run offline checks

Install in a clean environment and run:

```bash
python -m unittest -q
dynadot-api-tool --output json --version
dynadot-api-tool api3 --help
dynadot-api-tool domains availability --help
```

When checking write behavior, use simulated replies. A saved plan or simulated receipt shows what the CLI does under the tested conditions. Actual account permissions and prices must be checked with Dynadot for the specific action.
