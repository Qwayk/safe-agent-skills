---
title: serverPixel - GraphQL Admin
description: The server pixel configured by the app.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/serverPixel'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/serverPixel.md'
---

# server​Pixel

query

The server pixel configured by the app.

## Possible returns

* Server​Pixel

  [Server​Pixel](https://shopify.dev/docs/api/admin-graphql/latest/objects/ServerPixel)

  A server pixel stores configuration for streaming customer interactions to an EventBridge or PubSub endpoint.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * status

    [Server​Pixel​Status](https://shopify.dev/docs/api/admin-graphql/latest/enums/ServerPixelStatus)

    The current state of this server pixel.

  * webhook​Endpoint​Address

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    Address of the EventBridge or PubSub endpoint.

***

## Examples

* ### serverPixel reference
