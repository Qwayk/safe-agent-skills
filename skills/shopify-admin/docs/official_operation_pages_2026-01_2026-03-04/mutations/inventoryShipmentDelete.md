---
title: inventoryShipmentDelete - GraphQL Admin
description: Deletes an inventory shipment. Only draft shipments can be deleted.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventoryShipmentDelete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventoryShipmentDelete.md
---

# inventory​Shipment​Delete

mutation

Requires `write_inventory_shipments` access scope. Also: The user must have permission to manage inventory.

Deletes an inventory shipment. Only draft shipments can be deleted.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the inventory shipment to be deleted.

***

## Inventory​Shipment​Delete​Payload returns

* id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the inventory shipment that was deleted.

* user​Errors

  [\[Inventory​Shipment​Delete​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryShipmentDeleteUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### inventoryShipmentDelete reference
