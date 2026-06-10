---
title: marketWebPresenceDelete - GraphQL Admin
description: Deletes a market web presence.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketWebPresenceDelete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketWebPresenceDelete.md
---

# market​Web​Presence​Delete

mutation

Requires `read_markets` for queries and both `read_markets` as well as `write_markets` for mutations.

Deprecated. Use [webPresenceDelete](https://shopify.dev/docs/api/admin-graphql/latest/mutations/webPresenceDelete) instead.

Deletes a market web presence.

## Arguments

* web​Presence​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the web presence to delete.

***

## Market​Web​Presence​Delete​Payload returns

* deleted​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the deleted web presence.

* market

  [Market](https://shopify.dev/docs/api/admin-graphql/latest/objects/Market)

  The market for which the web presence was deleted.

* user​Errors

  [\[Market​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### marketWebPresenceDelete reference
