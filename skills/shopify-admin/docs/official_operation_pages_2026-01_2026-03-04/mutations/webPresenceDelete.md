---
title: webPresenceDelete - GraphQL Admin
description: Deletes a web presence.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/webPresenceDelete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/webPresenceDelete.md
---

# web​Presence​Delete

mutation

Requires `read_markets` for queries and both `read_markets` as well as `write_markets` for mutations.

Deletes a web presence.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the web presence to delete.

***

## Web​Presence​Delete​Payload returns

* deleted​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the deleted web presence.

* user​Errors

  [\[Market​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### webPresenceDelete reference
