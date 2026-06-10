---
title: deliveryPromiseParticipants - GraphQL Admin
description: Returns delivery promise participants.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/deliveryPromiseParticipants
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/deliveryPromiseParticipants.md
---

# delivery​Promise​Participants

query

Requires `read_delivery_promises` access scope.

Returns delivery promise participants.

## DeliveryPromiseParticipantConnection arguments

[DeliveryPromiseParticipantConnection](https://shopify.dev/docs/api/admin-graphql/latest/connections/DeliveryPromiseParticipantConnection)

* after

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* before

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* branded​Promise​Handle

  [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  The branded promise handle to filter by.

* first

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* last

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* owner​Ids

  [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The product variant ID to filter by.

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

***

## Possible returns

* edges

  [\[Delivery​Promise​Participant​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryPromiseParticipantEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Delivery​Promise​Participant!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryPromiseParticipant)

  non-null

  A list of nodes that are contained in DeliveryPromiseParticipantEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### deliveryPromiseParticipants reference
