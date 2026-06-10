---
title: inventoryShipmentCreate - GraphQL Admin
description: >-
  Adds a draft shipment to an inventory transfer.


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
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventoryShipmentCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventoryShipmentCreate.md
---

# inventory​Shipment​Create

mutation

Requires `write_inventory_shipments` access scope. Also: The user must have permission to manage inventory.

Adds a draft shipment to an inventory transfer.

***

**Caution:** As of 2026-01, this mutation supports an optional idempotency key using the \<code>@idempotent\</code> directive. As of 2026-04, the idempotency key is required and must be provided using the \<code>@idempotent\</code> directive. For more information, see the \<a href="https://shopify.dev/docs/api/usage/idempotent-requests">idempotency documentation\</a>.

***

## Arguments

* input

  [Inventory​Shipment​Create​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/InventoryShipmentCreateInput)

  required

  The input fields for the inventory shipment.

***

## Inventory​Shipment​Create​Payload returns

* inventory​Shipment

  [Inventory​Shipment](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryShipment)

  The created inventory shipment.

* user​Errors

  [\[Inventory​Shipment​Create​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryShipmentCreateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Creates a shipment with idempotency enabled (2026-01 onwards)

  #### Query

  ```graphql
  mutation inventoryShipmentCreate($input: InventoryShipmentCreateInput!, $idempotencyKey: String!) {
    inventoryShipmentCreate(input: $input) @idempotent(key: $idempotencyKey) {
      userErrors {
        field
        message
        code
      }
      inventoryShipment {
        id
        status
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "movementId": "gid://shopify/InventoryTransfer/208173983",
      "lineItems": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/113711323",
          "quantity": 420
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
  "query": "mutation inventoryShipmentCreate($input: InventoryShipmentCreateInput!, $idempotencyKey: String!) { inventoryShipmentCreate(input: $input) @idempotent(key: $idempotencyKey) { userErrors { field message code } inventoryShipment { id status } } }",
   "variables": {
      "input": {
        "movementId": "gid://shopify/InventoryTransfer/208173983",
        "lineItems": [
          {
            "inventoryItemId": "gid://shopify/InventoryItem/113711323",
            "quantity": 420
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
    mutation inventoryShipmentCreate($input: InventoryShipmentCreateInput!, $idempotencyKey: String!) {
      inventoryShipmentCreate(input: $input) @idempotent(key: $idempotencyKey) {
        userErrors {
          field
          message
          code
        }
        inventoryShipment {
          id
          status
        }
      }
    }`,
    {
      variables: {
          "input": {
              "movementId": "gid://shopify/InventoryTransfer/208173983",
              "lineItems": [
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/113711323",
                      "quantity": 420
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
    mutation inventoryShipmentCreate($input: InventoryShipmentCreateInput!, $idempotencyKey: String!) {
      inventoryShipmentCreate(input: $input) @idempotent(key: $idempotencyKey) {
        userErrors {
          field
          message
          code
        }
        inventoryShipment {
          id
          status
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "movementId": "gid://shopify/InventoryTransfer/208173983",
      "lineItems": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/113711323",
          "quantity": 420
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
      "query": `mutation inventoryShipmentCreate($input: InventoryShipmentCreateInput!, $idempotencyKey: String!) {
        inventoryShipmentCreate(input: $input) @idempotent(key: $idempotencyKey) {
          userErrors {
            field
            message
            code
          }
          inventoryShipment {
            id
            status
          }
        }
      }`,
      "variables": {
          "input": {
              "movementId": "gid://shopify/InventoryTransfer/208173983",
              "lineItems": [
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/113711323",
                      "quantity": 420
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
  'mutation inventoryShipmentCreate($input: InventoryShipmentCreateInput!, $idempotencyKey: String!) {
    inventoryShipmentCreate(input: $input) @idempotent(key: $idempotencyKey) {
      userErrors {
        field
        message
        code
      }
      inventoryShipment {
        id
        status
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "movementId": "gid://shopify/InventoryTransfer/208173983",
      "lineItems": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/113711323",
          "quantity": 420
        }
      ]
    },
    "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000"
  }'
  ```

  #### Response

  ```json
  {
    "inventoryShipmentCreate": {
      "userErrors": [],
      "inventoryShipment": {
        "id": "gid://shopify/InventoryShipment/787965982",
        "status": "DRAFT"
      }
    }
  }
  ```

* ### inventoryShipmentCreate reference
