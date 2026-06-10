---
title: serverPixelCreate - GraphQL Admin
description: >-
  Creates a new unconfigured server pixel. A single server pixel can exist for
  an app and shop combination. If you call this mutation when a server pixel
  already exists, then an error will return.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/serverPixelCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/serverPixelCreate.md
---

# server​Pixel​Create

mutation

Requires `write_pixels` access scope. Also: The app must have the read\_customer\_events access scope, write\_server\_pixels access scope, and user access permission.

Creates a new unconfigured server pixel. A single server pixel can exist for an app and shop combination. If you call this mutation when a server pixel already exists, then an error will return.

## Server​Pixel​Create​Payload returns

* server​Pixel

  [Server​Pixel](https://shopify.dev/docs/api/admin-graphql/latest/objects/ServerPixel)

  The new server pixel.

* user​Errors

  [\[Errors​Server​Pixel​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ErrorsServerPixelUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### serverPixelCreate reference
