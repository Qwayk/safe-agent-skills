# Jobs and batches

The current shipped CLI does not expose a generic jobs runner yet.

A generic batch runner would only be honest here after each batch action is backed by a real named Wix command family.

For now, use the real write commands in this tool one family at a time, with their normal plan-first flow.

## What to do instead

- Start with the exact command family you need from the shipped command guide.
- Save a plan with `--plan-out`.
- Review the plan before any live apply.
- Use `--apply --yes` only on the real write command you want.
- Save the receipt with `--receipt-out` after apply.

## Why this page stays in the docs

This page exists so future work on real batch support has one honest place to start from.
Until then, no generic CSV job actions are part of the public shipped surface.
