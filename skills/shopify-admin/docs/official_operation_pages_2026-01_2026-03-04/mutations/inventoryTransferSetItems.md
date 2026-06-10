---
title: inventoryTransferSetItems - GraphQL Admin
description: >-
  This mutation allows for the setting of line items on a Transfer. Will replace
  the items already set, if any.


  > Caution:

  > As of 2026-01, this mutation supports an optional idempotency key using the
  `@idempotent` directive.

  > As of 2026-04, the idempotency key is required and must be provided using
  the `@idempotent` directive.

  > For more information, see the [idempotency
  documentation](https://shopify.dev/docs/api/usage/idempotent-requests).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventoryTransferSetItems
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventoryTransferSetItems.md
---

# inventory​Transfer​Set​Items

mutation

Requires `write_inventory_transfers` access scope. Also: The user must have permission to manage inventory.

This mutation allows for the setting of line items on a Transfer. Will replace the items already set, if any.

***

**Caution:** As of 2026-01, this mutation supports an optional idempotency key using the \<code>@idempotent\</code> directive. As of 2026-04, the idempotency key is required and must be provided using the \<code>@idempotent\</code> directive. For more information, see the \<a href="https://shopify.dev/docs/api/usage/idempotent-requests">idempotency documentation\</a>.

***

## Arguments

* input

  [Inventory​Transfer​Set​Items​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/InventoryTransferSetItemsInput)

  required

  The input fields for the InventoryTransferSetItems mutation.

***

## Inventory​Transfer​Set​Items​Payload returns

* inventory​Transfer

  [Inventory​Transfer](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryTransfer)

  The Transfer with its line items updated.

* updated​Line​Items

  [\[Inventory​Transfer​Line​Item​Update!\]](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryTransferLineItemUpdate)

  The updated line items.

* user​Errors

  [\[Inventory​Transfer​Set​Items​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryTransferSetItemsUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Sets items on a transfer with idempotency enabled (2026-01 onwards)

  #### Query

  ```graphql
  mutation inventoryTransferSetItems($input: InventoryTransferSetItemsInput!, $idempotencyKey: String!) {
    inventoryTransferSetItems(input: $input) @idempotent(key: $idempotencyKey) {
      inventoryTransfer {
        id
      }
      updatedLineItems {
        inventoryItemId
        newQuantity
      }
      userErrors {
        field
        message
        code
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "id": "gid://shopify/InventoryTransfer/1061783017",
      "lineItems": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/498744621",
          "quantity": 2
        }
      ]
    },
    "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation inventoryTransferSetItems($input: InventoryTransferSetItemsInput!, $idempotencyKey: String!) { inventoryTransferSetItems(input: $input) @idempotent(key: $idempotencyKey) { inventoryTransfer { id } updatedLineItems { inventoryItemId newQuantity } userErrors { field message code } } }",
   "variables": {
      "input": {
        "id": "gid://shopify/InventoryTransfer/1061783017",
        "lineItems": [
          {
            "inventoryItemId": "gid://shopify/InventoryItem/498744621",
            "quantity": 2
          }
        ]
      },
      "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000"
    }
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    mutation inventoryTransferSetItems($input: InventoryTransferSetItemsInput!, $idempotencyKey: String!) {
      inventoryTransferSetItems(input: $input) @idempotent(key: $idempotencyKey) {
        inventoryTransfer {
          id
        }
        updatedLineItems {
          inventoryItemId
          newQuantity
        }
        userErrors {
          field
          message
          code
        }
      }
    }`,
    {
      variables: {
          "input": {
              "id": "gid://shopify/InventoryTransfer/1061783017",
              "lineItems": [
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/498744621",
                      "quantity": 2
                  }
              ]
          },
          "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000"
      },
    },
    );
    const json = await response.json();
    return json.data;
  }
  ```

  #### Ruby

  ```ruby
  session = ShopifyAPI::Auth::Session.new(
    shop: "your-development-store.myshopify.com",
    access_token: access_token
  )
  client = ShopifyAPI::Clients::Graphql::Admin.new(
    session: session
  )

  query = <<~QUERY
    mutation inventoryTransferSetItems($input: InventoryTransferSetItemsInput!, $idempotencyKey: String!) {
      inventoryTransferSetItems(input: $input) @idempotent(key: $idempotencyKey) {
        inventoryTransfer {
          id
        }
        updatedLineItems {
          inventoryItemId
          newQuantity
        }
        userErrors {
          field
          message
          code
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "id": "gid://shopify/InventoryTransfer/1061783017",
      "lineItems": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/498744621",
          "quantity": 2
        }
      ]
    },
    "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation inventoryTransferSetItems($input: InventoryTransferSetItemsInput!, $idempotencyKey: String!) {
        inventoryTransferSetItems(input: $input) @idempotent(key: $idempotencyKey) {
          inventoryTransfer {
            id
          }
          updatedLineItems {
            inventoryItemId
            newQuantity
          }
          userErrors {
            field
            message
            code
          }
        }
      }`,
      "variables": {
          "input": {
              "id": "gid://shopify/InventoryTransfer/1061783017",
              "lineItems": [
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/498744621",
                      "quantity": 2
                  }
              ]
          },
          "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation inventoryTransferSetItems($input: InventoryTransferSetItemsInput!, $idempotencyKey: String!) {
    inventoryTransferSetItems(input: $input) @idempotent(key: $idempotencyKey) {
      inventoryTransfer {
        id
      }
      updatedLineItems {
        inventoryItemId
        newQuantity
      }
      userErrors {
        field
        message
        code
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "id": "gid://shopify/InventoryTransfer/1061783017",
      "lineItems": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/498744621",
          "quantity": 2
        }
      ]
    },
    "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000"
  }'
  ```

  #### Response

  ```json
  {
    "inventoryTransferSetItems": {
      "inventoryTransfer": {
        "id": "gid://shopify/InventoryTransfer/1061783017"
      },
      "updatedLineItems": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/498744621",
          "newQuantity": 2
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### inventoryTransferSetItems reference
