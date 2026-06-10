---
title: segmentCreate - GraphQL Admin
description: Creates a segment.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/segmentCreate'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/segmentCreate.md'
---

# segment​Create

mutation

Requires `write_customers` access scope. Also: The user must not have restricted access.

Creates a segment.

## Arguments

* name

  [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  The name of the segment to be created. Segment names must be unique.

* query

  [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  A precise definition of the segment. The definition is composed of a combination of conditions on facts about customers such as `email_subscription_status = 'SUBSCRIBED'` with [this syntax](https://shopify.dev/api/shopifyql/segment-query-language-reference).

***

## Segment​Create​Payload returns

* segment

  [Segment](https://shopify.dev/docs/api/admin-graphql/latest/objects/Segment)

  The newly created segment.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### segmentCreate reference
