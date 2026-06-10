---
title: inventoryTransferCancel - GraphQL Admin
description: Cancels an inventory transfer.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventoryTransferCancel
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventoryTransferCancel.md
---

# inventory​Transfer​Cancel

mutation

Requires `write_inventory_transfers` access scope. Also: The user must have permission to manage inventory.

Cancels an inventory transfer.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the inventory transfer to cancel.

***

## Inventory​Transfer​Cancel​Payload returns

* inventory​Transfer

  [Inventory​Transfer](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryTransfer)

  The cancelled inventory transfer.

* user​Errors

  [\[Inventory​Transfer​Cancel​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryTransferCancelUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### inventoryTransferCancel reference
