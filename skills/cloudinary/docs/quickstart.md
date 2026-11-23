# Quickstart

## Install and read one image

If your agent already has the command-line tool, start with setup. To install it from a download, open the Cloudinary tool folder containing `pyproject.toml`. Use Python 3.12 or newer.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
cloudinary-safe-agent-cli --version
```

Run setup and add your media library's cloud name, API key, and API secret to the local settings file it names. [Connect Cloudinary](onboarding.md) explains how to find them.

```bash
cloudinary-safe-agent-cli onboarding
cloudinary-safe-agent-cli operations admin resources-get-resources \
  --path-param resource_type=image --query max_results=1
```

Check the result against the library you intended to open. Use `resource_type=video` for a video. If the library is empty, an empty list is a valid result. For a specific asset, use [the asset lookup example](command_reference.md#read-one-asset).

You can also ask the agent to find folders, tags, upload presets, or streaming settings. Account-level work such as reading user roles uses a separate connection.

## Preview an upload

Edit the [multipart example](../examples/multipart-upload.sample.json) to name the local file and the Cloudinary public ID you want. Save your copy as `upload.json` and run:

```bash
cloudinary-safe-agent-cli --plan-out upload-plan.json operations upload upload-signed \
  --multipart-spec-file upload.json
```

Check the library, public ID, and file in the preview. A signed upload keeps an existing file with the same public ID by default. When you're ready to apply, follow [Approve and check changes](safety_model.md).

For several files, use a named bulk command where Cloudinary offers one. For separate actions, keep a plan and result for each operation so you can see which ones ran.
