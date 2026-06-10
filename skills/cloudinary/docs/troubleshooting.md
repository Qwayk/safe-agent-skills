# Troubleshooting

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
