---
title: customerSegmentMembership - GraphQL Admin
description: 'Whether a member, which is a customer, belongs to a segment.'
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/customerSegmentMembership
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/customerSegmentMembership.md
---

# customer​Segment​Membership

query

Whether a member, which is a customer, belongs to a segment.

## Arguments

* customer​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the customer that has the membership.

* segment​Ids

  [\[ID!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The segments to evaluate for the given customer.

***

## Possible returns

* Segment​Membership​Response

  [Segment​Membership​Response!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SegmentMembershipResponse)

  A list of maps that contain `segmentId` IDs and `isMember` Booleans. The maps represent segment memberships.

  * memberships

    [\[Segment​Membership!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SegmentMembership)

    non-null

    The membership status for the given list of segments.

***

## Examples

* ### customerSegmentMembership reference
