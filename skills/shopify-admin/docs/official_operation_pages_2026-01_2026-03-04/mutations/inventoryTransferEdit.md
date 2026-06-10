---
title: inventoryTransferEdit - GraphQL Admin
description: Edits an inventory transfer.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventoryTransferEdit
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventoryTransferEdit.md
---

# inventory​Transfer​Edit

mutation

Requires `write_inventory_transfers` access scope. Also: The user must have permission to manage inventory.

Edits an inventory transfer.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the inventory Transfer to be edited.

* input

  [Inventory​Transfer​Edit​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/InventoryTransferEditInput)

  required

  The input fields to edit the inventory transfer.

***

## Inventory​Transfer​Edit​Payload returns

* inventory​Transfer

  [Inventory​Transfer](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryTransfer)

  The edited inventory transfer.

* user​Errors

  [\[Inventory​Transfer​Edit​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryTransferEditUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### inventoryTransferEdit reference
