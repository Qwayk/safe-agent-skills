---
title: segmentDelete - GraphQL Admin
description: Deletes a segment.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/segmentDelete'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/segmentDelete.md'
---

# segment​Delete

mutation

Requires `write_customers` access scope. Also: The user must not have restricted access.

Deletes a segment.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  Specifies the segment to delete.

***

## Segment​Delete​Payload returns

* deleted​Segment​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  ID of the deleted segment.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### segmentDelete reference
