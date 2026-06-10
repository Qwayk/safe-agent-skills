---
title: inventoryTransferMarkAsReadyToShip - GraphQL Admin
description: Sets an inventory transfer to ready to ship.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventoryTransferMarkAsReadyToShip
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventoryTransferMarkAsReadyToShip.md
---

# inventory​Transfer​Mark​As​Ready​To​Ship

mutation

Requires `write_inventory_transfers` access scope. Also: The user must have permission to manage inventory.

Sets an inventory transfer to ready to ship.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the inventory transfer to mark as ready to ship.

***

## Inventory​Transfer​Mark​As​Ready​To​Ship​Payload returns

* inventory​Transfer

  [Inventory​Transfer](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryTransfer)

  The ready to ship inventory transfer.

* user​Errors

  [\[Inventory​Transfer​Mark​As​Ready​To​Ship​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryTransferMarkAsReadyToShipUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### inventoryTransferMarkAsReadyToShip reference
