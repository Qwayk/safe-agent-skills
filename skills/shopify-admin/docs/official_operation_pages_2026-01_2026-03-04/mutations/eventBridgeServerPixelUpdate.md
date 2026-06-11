---
title: eventBridgeServerPixelUpdate - GraphQL Admin
description: |-
  Updates the server pixel to connect to an EventBridge endpoint.
  Running this mutation deletes any previous subscriptions for the server pixel.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/eventBridgeServerPixelUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/eventBridgeServerPixelUpdate.md
---

# event​Bridge​Server​Pixel​Update

mutation

Requires `write_pixels` access scope. Also: The app must have the read\_customer\_events and write\_server\_pixels access scopes.

Updates the server pixel to connect to an EventBridge endpoint. Running this mutation deletes any previous subscriptions for the server pixel.

## Arguments

* arn

  [ARN!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ARN)

  required

  The ARN for the EventBridge endpoint to which customer events are to be sent.

***

## Event​Bridge​Server​Pixel​Update​Payload returns

* server​Pixel

  [Server​Pixel](https://shopify.dev/docs/api/admin-graphql/latest/objects/ServerPixel)

  The server pixel as configured by the mutation.

* user​Errors

  [\[Errors​Server​Pixel​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ErrorsServerPixelUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### eventBridgeServerPixelUpdate reference
