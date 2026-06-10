---
title: pubSubServerPixelUpdate - GraphQL Admin
description: |-
  Updates the server pixel to connect to a Google PubSub endpoint.
  Running this mutation deletes any previous subscriptions for the server pixel.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/pubSubServerPixelUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/pubSubServerPixelUpdate.md
---

# pub​Sub​Server​Pixel​Update

mutation

Requires `write_pixels` access scope. Also: The app must have the read\_customer\_events and write\_server\_pixels access scopes.

Updates the server pixel to connect to a Google PubSub endpoint. Running this mutation deletes any previous subscriptions for the server pixel.

## Arguments

* pub​Sub​Project

  [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  The Google PubSub project ID.

* pub​Sub​Topic

  [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  The Google PubSub topic ID.

***

## Pub​Sub​Server​Pixel​Update​Payload returns

* server​Pixel

  [Server​Pixel](https://shopify.dev/docs/api/admin-graphql/latest/objects/ServerPixel)

  The server pixel as configured by the mutation.

* user​Errors

  [\[Errors​Server​Pixel​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ErrorsServerPixelUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### pubSubServerPixelUpdate reference
