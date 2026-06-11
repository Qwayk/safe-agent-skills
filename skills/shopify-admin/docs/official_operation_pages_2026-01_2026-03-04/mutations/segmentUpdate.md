---
title: segmentUpdate - GraphQL Admin
description: Updates a segment.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/segmentUpdate'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/segmentUpdate.md'
---

# segment​Update

mutation

Requires `write_customers` access scope. Also: The user must not have restricted access.

Updates a segment.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  Specifies the segment to be updated.

* name

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The new name for the segment.

* query

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  A precise definition of the segment. The definition is composed of a combination of conditions on facts about customers such as `email_subscription_status = 'SUBSCRIBED'` with [this syntax](https://shopify.dev/api/shopifyql/segment-query-language-reference).

***

## Segment​Update​Payload returns

* segment

  [Segment](https://shopify.dev/docs/api/admin-graphql/latest/objects/Segment)

  The updated segment.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### segmentUpdate reference
