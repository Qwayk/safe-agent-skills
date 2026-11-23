# Quickstart

## Install and read a file

If your agent already has the command-line tool, start with setup. To install it yourself, open the downloaded Figma tool folder, which contains `pyproject.toml`. Use Python 3.12 or newer.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
figma-safe-agent-cli --version
```

Run setup. Open the settings file it names and add your Figma token there. See [Connect Figma](onboarding.md) if you use OAuth or a plan token.

```bash
figma-safe-agent-cli onboarding
figma-safe-agent-cli operations files get-file-meta --file-key YOUR_FILE_KEY
```

The file key comes after `figma.com/design/` in a design link. The file name in the result should match the design you meant to open.

## Review a design or get images

Ask your agent to read the comments and version history, review components and styles in a team library, or look up variables and webhooks. Give it the file, team, or project link you want it to use.

To get a PNG link for a frame, use its node ID. You can pass several IDs separated by commas.

```bash
figma-safe-agent-cli operations files render-images --file-key YOUR_FILE_KEY --ids 1:2,1:3 --format png --out images.json
```

The command tells you which nodes got links and which failed. `images.json` holds Figma's reply with temporary links. Open or download the images while those links still work. Figma can fail to render an individual node, for example if it is missing or invisible. [Figma image docs](https://developers.figma.com/docs/rest-api/file-endpoints/#get-image)

## Preview a comment

Put the exact comment in `body.json`, for example `{"message":"Can we confirm this button label?"}`.

```bash
figma-safe-agent-cli --plan-out comment-plan.json operations comments post-comment --file-key YOUR_FILE_KEY --body-json-file body.json
```

Ask the agent to show you the file and comment text. When you are ready to post it, follow [Approve and check changes](safety_model.md). The [command guide](command_reference.md) has options for other commands.
