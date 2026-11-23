# What we tested

## November 23, 2026 local checks

Both fresh installs passed 48 offline tests and listed 250 commands from the June list. The 23 retired Assistants commands stop on the machine with a link to OpenAI’s migration guide. Setup created a private settings file in a new folder and printed the check for that file. A simulated model read used the installed package.

Offline tests checked a changed key, project, settings folder, and upload. They also checked that the receipt exists before sending, the same approval cannot send twice, and a missing reply leaves a record to inspect. A response creation checked its specific ID. A free moderation call used the ordinary approval without the spending flag and skipped an unrelated read. The routine run summary and log contain the operation name without the prompt.

The wheel and source archive include the skill and command list. The source archive also includes the dated references. All six JSON examples worked. The source has 36 working local links and the catalog copy has 31. I checked that the four March files in GitHub history match the originals byte for byte. All OpenAI API checks used simulated replies.

Ruff passed for the edited Python files. The full type check reported the same 15 findings before and after this change.

## June 29, 2026 checks

The June refresh matched 273 operation rows in the pinned list, coverage, and saved example. The builder ran `python3 src/openai_api_tool/scripts/refresh_official_inventory.py --date 2026-06-29` and `.venv/bin/python -m unittest -q`. All 41 tests passed on the source and the public copy. The review also confirmed that ordinary API writes required `--plan-in`. [June GitHub release](https://github.com/Qwayk/safe-agent-skills/commit/337a6c5620c708deea2ce43d9af187074e811651)

## March 2026 checks

The March 14 release fixed missing docs and catalog links. The March 15 pass added local files for streaming and binary replies, redaction for JSON previews, and checks for changes to saved plan inputs. It kept those checks local because the tool did not have a documented provider guarantee against repeat sends.

[June and March source files](references.md) · [Local examples](examples/)
