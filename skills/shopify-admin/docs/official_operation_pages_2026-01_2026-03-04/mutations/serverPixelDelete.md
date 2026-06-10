---
title: serverPixelDelete - GraphQL Admin
description: Deletes the Server Pixel associated with the current app & shop.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/serverPixelDelete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/serverPixelDelete.md
---

# server​Pixel​Delete

mutation

Requires `write_pixels` access scope. Also: The app must have the write\_server\_pixels access scope, and user access permission.

Deletes the Server Pixel associated with the current app & shop.

## Server​Pixel​Delete​Payload returns

* deleted​Server​Pixel​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the server pixel that was deleted, if one was deleted.

* user​Errors

  [\[Errors​Server​Pixel​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ErrorsServerPixelUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### serverPixelDelete reference
