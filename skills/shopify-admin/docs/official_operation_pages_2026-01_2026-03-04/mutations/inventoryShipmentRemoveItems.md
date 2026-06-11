---
title: inventoryShipmentRemoveItems - GraphQL Admin
description: Remove items from an inventory shipment.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventoryShipmentRemoveItems
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventoryShipmentRemoveItems.md
---

# inventory​Shipment​Remove​Items

mutation

Requires `write_inventory_shipments` access scope. Also: The user must have permission to manage inventory.

Remove items from an inventory shipment.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the inventory shipment to remove items from.

* line​Items

  [\[ID!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  A list of inventory shipment line item ids representing the items to be removed from the shipment.

***

## Inventory​Shipment​Remove​Items​Payload returns

* inventory​Shipment

  [Inventory​Shipment](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryShipment)

  The inventory shipment with items removed.

* user​Errors

  [\[Inventory​Shipment​Remove​Items​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryShipmentRemoveItemsUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### inventoryShipmentRemoveItems reference
