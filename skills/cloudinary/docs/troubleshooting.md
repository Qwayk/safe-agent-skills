# Troubleshooting

When Cloudinary stops or returns an error, start with the boring checks first: setup, account access, target IDs, API limits, and the tool's safety gates. That usually tells you whether the problem is local configuration, provider permissions, a bad request, or a write that correctly refused to run.

Keep the JSON error output. It is the best clue for an agent reviewing media assets, folders, tags, transformations, and delivery settings, and it is safer than retrying commands blindly. For any write-related error, stop before retrying and confirm the needed approval or plan.

A good first troubleshooting ask is: "Read the Cloudinary error, explain what failed in plain English, tell me the safest next check, and do not retry any write or destructive action."

## `auth check` says product setup is missing

Check:
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

## `auth check` says account setup is missing

Check:
- `CLOUDINARY_ACCOUNT_ID`
- `CLOUDINARY_ACCOUNT_API_KEY`
- `CLOUDINARY_ACCOUNT_API_SECRET`

## Cloudinary uses a regional host

Set the matching host:
- `CLOUDINARY_PRODUCT_API_HOST`
- `CLOUDINARY_ACCOUNT_API_HOST`

## A command says `Missing path param`

Use `operations show --area ... --op ...` and check the path template.
Then add each missing name with `--path-param key=value`.

## A command says `This Cloudinary operation requires a request body`

Use one of:
- `--body-json-file`
- `--form-field`
- `--multipart-spec-file`

## A command refuses to print output

That operation is marked sensitive or binary.
Run it again with `--out`, and keep the path inside `--project-dir`.

## You need more HTTP detail

Add `--verbose` to see request start and end lines on stderr.
Add `--debug` only when you need a Python stack trace.
