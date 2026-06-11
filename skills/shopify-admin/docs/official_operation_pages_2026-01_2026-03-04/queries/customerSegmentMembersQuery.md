---
title: customerSegmentMembersQuery - GraphQL Admin
description: Returns a `CustomerSegmentMembersQuery` resource by ID.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/customerSegmentMembersQuery
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/customerSegmentMembersQuery.md
---

# customer​Segment​Members​Query

query

Returns a `CustomerSegmentMembersQuery` resource by ID.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the `CustomerSegmentMembersQuery` to return.

***

## Possible returns

* Customer​Segment​Members​Query

  [Customer​Segment​Members​Query](https://shopify.dev/docs/api/admin-graphql/latest/objects/CustomerSegmentMembersQuery)

  A job to determine a list of members, such as customers, that are associated with an individual segment.

  * current​Count

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    The current total number of members in a given segment.

  * done

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    This indicates if the job is still queued or has been run.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID that's returned when running an asynchronous mutation.

***

## Examples

* ### customerSegmentMembersQuery reference
