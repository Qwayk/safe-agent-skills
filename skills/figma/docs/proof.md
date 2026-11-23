# Figma test results

## November 23, 2026

Built the repo and public packages and installed each in a fresh Python environment. Each passed 38 tests and loaded all 51 named operations.

The installed-tool checks used simulated Figma replies. Setup created the settings file without a separate template. One file read worked with the profile permission absent, and a denied file read failed. When one of two frames failed to render, the output named the missing frame and saved the links Figma returned.

I checked all 11 write commands with local plans. A saved plan for the same request and connection passed. Missing plans, older plans and plans made without a connection stopped before a change was sent. The tests also covered changes to the file, comment text and token, and checked that receipts reported different comment text and missing comment lists accurately.

Live account access and provider-side changes still need a real Figma connection to verify.

## June 4, 2026

The earlier local check used version `0.1.0` and the Figma docs listed in [References](references.md). It checked operation listing, token checks, named request options, write approvals and saving output. The files below are saved samples from that check. The successful profile check used a simulated reply.

- [Version](examples/outputs/version.json)
- [Profile check](examples/outputs/auth_check.json)
- [List file commands](examples/outputs/operations_list_files.json)
- [Show the post-comment command](examples/outputs/operations_show_post_comment.json)
- [Read file nodes](examples/outputs/get_file_nodes.json)
- [Preview a comment](examples/outputs/post_comment_dry_run.json)
- [Comment apply stopped for approval to proceed without a saved before-state](examples/outputs/post_comment_apply.json)
- [Example plan](examples/plan.example.json) and [example receipt](examples/receipt.example.json)

The tool includes `/v1/discovery` from Figma's developer docs. At the June 4 check it was absent from Figma's published OpenAPI file.
