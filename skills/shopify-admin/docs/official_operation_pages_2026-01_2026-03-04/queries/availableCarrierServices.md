---
title: availableCarrierServices - GraphQL Admin
description: >-
  Returns a list of activated carrier services and associated shop locations
  that support them.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/availableCarrierServices
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/availableCarrierServices.md
---

# available​Carrier​Services

query

Returns a list of activated carrier services and associated shop locations that support them.

## Possible returns

* Delivery​Carrier​Service​And​Locations

  [\[Delivery​Carrier​Service​And​Locations!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryCarrierServiceAndLocations)

  Links a [`DeliveryCarrierService`](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryCarrierService) with the associated shop [locations](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location) where it can calculate shipping rates. Each pairing indicates the locations that can use a specific carrier service for real-time rate calculations during checkout.

  The carrier service provides the shipping rate calculation logic, while the locations represent physical or virtual fulfillment points that can ship orders using that service.

  * carrier​Service

    [Delivery​Carrier​Service!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryCarrierService)

    non-null

    The carrier service.

  * locations

    [\[Location!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location)

    non-null

    The list of locations that support this carrier service.

***

## Examples

* ### availableCarrierServices reference
