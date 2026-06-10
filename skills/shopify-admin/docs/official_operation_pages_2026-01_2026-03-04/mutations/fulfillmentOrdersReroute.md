---
title: fulfillmentOrdersReroute - GraphQL Admin
description: >-
  Route the fulfillment orders to an alternative location, according to the
  shop's order routing settings. This involves:

  * Finding an alternate location that can fulfill the fulfillment orders.

  * Assigning the fulfillment orders to the new location.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentOrdersReroute
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentOrdersReroute.md
---

# fulfillment​Orders​Reroute

mutation

Requires `write_assigned_fulfillment_orders` access scope, `write_merchant_managed_fulfillment_orders` access scope or `write_third_party_fulfillment_orders` access scope. Also: The user must have the fulfill\_and\_ship\_orders permission or the calling API client must be Shopify POS.

Route the fulfillment orders to an alternative location, according to the shop's order routing settings. This involves:

* Finding an alternate location that can fulfill the fulfillment orders.
* Assigning the fulfillment orders to the new location.

## Arguments

* excluded​Location​Ids

  [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The list of IDs of the locations to exclude for rerouting. Excluded locations specified here take precedence over included locations provided through included\_location\_ids.

* fulfillment​Order​Ids

  [\[ID!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The list of IDs of the fulfillment orders.

* included​Location​Ids

  [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The list of IDs of the locations to include for rerouting. By default, all locations are included.

***

## Fulfillment​Orders​Reroute​Payload returns

* moved​Fulfillment​Orders

  [\[Fulfillment​Order!\]](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrder)

  The fulfillment orders which contains the moved line items.

* user​Errors

  [\[Fulfillment​Orders​Reroute​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrdersRerouteUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### fulfillmentOrdersReroute reference
