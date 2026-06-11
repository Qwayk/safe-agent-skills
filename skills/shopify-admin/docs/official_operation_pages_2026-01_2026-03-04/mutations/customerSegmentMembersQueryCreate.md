---
title: customerSegmentMembersQueryCreate - GraphQL Admin
description: Creates a customer segment members query.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerSegmentMembersQueryCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerSegmentMembersQueryCreate.md
---

# customer​Segment​Members​Query​Create

mutation

Requires `write_customers` access scope.

Creates a customer segment members query.

## Arguments

* input

  [Customer​Segment​Members​Query​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CustomerSegmentMembersQueryInput)

  required

  The input fields to create a customer segment members query.

***

## Customer​Segment​Members​Query​Create​Payload returns

* customer​Segment​Members​Query

  [Customer​Segment​Members​Query](https://shopify.dev/docs/api/admin-graphql/latest/objects/CustomerSegmentMembersQuery)

  The newly created customer segment members query.

* user​Errors

  [\[Customer​Segment​Members​Query​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CustomerSegmentMembersQueryUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### customerSegmentMembersQueryCreate reference
