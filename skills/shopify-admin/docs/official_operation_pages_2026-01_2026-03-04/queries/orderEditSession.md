---
title: orderEditSession - GraphQL Admin
description: Returns a `OrderEditSession` resource by ID.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/orderEditSession'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/orderEditSession.md
---

# order​Edit​Session

query

Returns a `OrderEditSession` resource by ID.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the `OrderEditSession` to return.

***

## Possible returns

* Order​Edit​Session

  [Order​Edit​Session](https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderEditSession)

  An edit session for an order.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    The unique ID of the order edit session.

***

## Examples

* ### orderEditSession reference
