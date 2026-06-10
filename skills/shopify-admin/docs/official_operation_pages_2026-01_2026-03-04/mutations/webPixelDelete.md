---
title: webPixelDelete - GraphQL Admin
description: Deletes the web pixel shop settings.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/webPixelDelete'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/webPixelDelete.md
---

# web​Pixel​Delete

mutation

Requires `write_pixels` access scope. Also: The app requires user access permission.

Deletes the web pixel shop settings.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the web pixel to delete.

***

## Web​Pixel​Delete​Payload returns

* deleted​Web​Pixel​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the web pixel settings that was deleted.

* user​Errors

  [\[Errors​Web​Pixel​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ErrorsWebPixelUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### webPixelDelete reference
