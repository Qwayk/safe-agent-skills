# What we checked

## November 23, 2026

Both local copies passed 41 offline tests with simulated Freepik replies. I also installed each copy in a clean Python environment, ran the installed command, and repeated the seven download and setup tests against the installed code. The full test suite checks startup with an account configured, selection of the asset preview, and exclusion of photos with missing or mismatched AI fields. Changing the account, file destination, asset, size or CSV rows blocks the license request until there is a new saved preview.

The tests send a license request once on a timeout or HTTP 503. They check that the inventory keeps the license link, download ID, file format and hash when a file is saved. They also check that a failed second file keeps the first file and its row and that a batch leaves the remaining jobs untouched.

## Earlier checks

The earlier proof summary was dated June 11, 2026. The work tracked in issue #50 added the proof examples, required one JSON object on stdout even for usage errors, and checked refusal on unknown AI flags, repeat downloads and overwrites.

The saved [plan](examples/plan.example.json), [receipt](examples/receipt.example.json) and [command outputs](examples/outputs/) show the earlier result format. Save a new preview with `--plan-out` for any new download. The old plan examples predate the matching account and request check.

## Run the checks

Run `python3 -m unittest -q` from the package folder. Use `freepik-api-tool --output json --version` to check the installed command. For an authorized account check, use `freepik-api-tool auth check` to make one search. See the [developer guide](development.md) and [download approval steps](safety_model.md) before trying a licensed download.
