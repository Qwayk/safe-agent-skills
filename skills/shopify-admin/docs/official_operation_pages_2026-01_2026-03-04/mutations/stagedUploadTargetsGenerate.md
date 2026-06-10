---
title: stagedUploadTargetsGenerate - GraphQL Admin
description: Uploads multiple images.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/stagedUploadTargetsGenerate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/stagedUploadTargetsGenerate.md
---

# staged​Upload​Targets​Generate

mutation

Deprecated. Use [stagedUploadsCreate](https://shopify.dev/docs/api/admin-graphql/latest/mutations/stagedUploadsCreate) instead.

Uploads multiple images.

## Arguments

* input

  [\[Stage​Image​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/StageImageInput)

  required

  The input fields for generating staged uploads.

***

## Staged​Upload​Targets​Generate​Payload returns

* urls

  [\[Staged​Upload​Target!\]](https://shopify.dev/docs/api/admin-graphql/latest/objects/StagedUploadTarget)

  The staged upload targets that were generated.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### stagedUploadTargetsGenerate reference
