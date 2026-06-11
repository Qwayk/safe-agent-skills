---
title: inventoryTransferDuplicate - GraphQL Admin
description: >-
  This mutation allows duplicating an existing inventory transfer. The
  duplicated transfer will have the same

  line items and quantities as the original transfer, but will be in a draft
  state with no shipments.


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
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventoryTransferDuplicate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventoryTransferDuplicate.md
---

# inventory​Transfer​Duplicate

mutation

Requires `write_inventory_transfers` access scope. Also: The user must have permission to manage inventory.

This mutation allows duplicating an existing inventory transfer. The duplicated transfer will have the same line items and quantities as the original transfer, but will be in a draft state with no shipments.

***

**Caution:** As of 2026-01, this mutation supports an optional idempotency key using the \<code>@idempotent\</code> directive. As of 2026-04, the idempotency key is required and must be provided using the \<code>@idempotent\</code> directive. For more information, see the \<a href="https://shopify.dev/docs/api/usage/idempotent-requests">idempotency documentation\</a>.

***

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the inventory transfer to duplicate.

***

## Inventory​Transfer​Duplicate​Payload returns

* inventory​Transfer

  [Inventory​Transfer](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryTransfer)

  The duplicated inventory transfer.

* user​Errors

  [\[Inventory​Transfer​Duplicate​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryTransferDuplicateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Duplicates a transfer with idempotency enabled (2026-01 onwards)

  #### Query

  ```graphql
  mutation inventoryTransferDuplicate($id: ID!, $idempotencyKey: String!) {
    inventoryTransferDuplicate(id: $id) @idempotent(key: $idempotencyKey) {
      inventoryTransfer {
        id
      }
      userErrors {
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/InventoryTransfer/825890269",
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
  "query": "mutation inventoryTransferDuplicate($id: ID!, $idempotencyKey: String!) { inventoryTransferDuplicate(id: $id) @idempotent(key: $idempotencyKey) { inventoryTransfer { id } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/InventoryTransfer/825890269",
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
    mutation inventoryTransferDuplicate($id: ID!, $idempotencyKey: String!) {
      inventoryTransferDuplicate(id: $id) @idempotent(key: $idempotencyKey) {
        inventoryTransfer {
          id
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/InventoryTransfer/825890269",
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
    mutation inventoryTransferDuplicate($id: ID!, $idempotencyKey: String!) {
      inventoryTransferDuplicate(id: $id) @idempotent(key: $idempotencyKey) {
        inventoryTransfer {
          id
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/InventoryTransfer/825890269",
    "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation inventoryTransferDuplicate($id: ID!, $idempotencyKey: String!) {
        inventoryTransferDuplicate(id: $id) @idempotent(key: $idempotencyKey) {
          inventoryTransfer {
            id
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/InventoryTransfer/825890269",
          "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation inventoryTransferDuplicate($id: ID!, $idempotencyKey: String!) {
    inventoryTransferDuplicate(id: $id) @idempotent(key: $idempotencyKey) {
      inventoryTransfer {
        id
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/InventoryTransfer/825890269",
    "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000"
  }'
  ```

  #### Response

  ```json
  {
    "inventoryTransferDuplicate": {
      "inventoryTransfer": {
        "id": "gid://shopify/InventoryTransfer/1061783019"
      },
      "userErrors": []
    }
  }
  ```

* ### inventoryTransferDuplicate reference
