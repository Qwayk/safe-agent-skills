# Proof and verification

## November 23, 2026 local checks

Both clean Python installs passed 52 offline tests. Installing the local release as a Codex skill under `amazon-creators` matched all 65 files. Both skill instruction files and the guide links passed their checks.

Starting in an empty folder, the installed CLI created a private settings file and got a token from a simulated Amazon reply. It used the selected account when a shell setting disagreed, kept tokens for separate files apart, and left the previous token in place after a failed refresh. The search checked a saved preview before sending a request, returned product links and the match count, and distinguished a partial reply from a denial or an empty search.

These checks used fake credentials and replies. They establish how the local tool handles setup and results. Amazon catalog access still needs a live check with an eligible account.

## June 4, 2026 checks

The earlier version passed 47 unit tests, alongside compile, version, example JSON, catalog preview, and local helper refusal checks. The local token and file creation commands in that version could preview work and refused apply.

The examples below come from the earlier version. Generate a new preview with the current tool when you want to run a checked search.

- [Sign-in check](examples/outputs/auth_check.json)
- [Search results](examples/outputs/search.json)
- [Item details](examples/outputs/items.json)
- [Book and media details](examples/outputs/items-book-media.json)
- [Variations](examples/outputs/variations.json)
- [Category details](examples/outputs/browse-nodes.json)
- [Saved preview](examples/plan.example.json) and [receipt](examples/receipt.example.json)
