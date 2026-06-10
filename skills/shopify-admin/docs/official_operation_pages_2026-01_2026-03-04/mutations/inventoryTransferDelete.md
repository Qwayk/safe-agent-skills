---
title: inventoryTransferDelete - GraphQL Admin
description: Deletes an inventory transfer.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventoryTransferDelete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventoryTransferDelete.md
---

# inventory​Transfer​Delete

mutation

Requires `write_inventory_transfers` access scope. Also: The user must have permission to manage inventory.

Deletes an inventory transfer.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the inventory transfer to delete.

***

## Inventory​Transfer​Delete​Payload returns

* deleted​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the deleted inventory transfer.

* user​Errors

  [\[Inventory​Transfer​Delete​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryTransferDeleteUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### inventoryTransferDelete reference
