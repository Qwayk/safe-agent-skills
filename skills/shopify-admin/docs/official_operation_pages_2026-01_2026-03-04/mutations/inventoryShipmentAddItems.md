---
title: inventoryShipmentAddItems - GraphQL Admin
description: >-
  Adds items to an inventory shipment.


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
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventoryShipmentAddItems
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventoryShipmentAddItems.md
---

# inventory​Shipment​Add​Items

mutation

Requires `write_inventory_shipments` access scope. Also: The user must have permission to manage inventory.

Adds items to an inventory shipment.

***

**Caution:** As of 2026-01, this mutation supports an optional idempotency key using the \<code>@idempotent\</code> directive. As of 2026-04, the idempotency key is required and must be provided using the \<code>@idempotent\</code> directive. For more information, see the \<a href="https://shopify.dev/docs/api/usage/idempotent-requests">idempotency documentation\</a>.

***

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the inventory shipment to modify.

* line​Items

  [\[Inventory​Shipment​Line​Item​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/InventoryShipmentLineItemInput)

  required

  The list of line items to add to the inventory shipment.

***

## Inventory​Shipment​Add​Items​Payload returns

* added​Items

  [\[Inventory​Shipment​Line​Item!\]](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryShipmentLineItem)

  The list of added line items.

* inventory​Shipment

  [Inventory​Shipment](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryShipment)

  The inventory shipment with the added items.

* user​Errors

  [\[Inventory​Shipment​Add​Items​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryShipmentAddItemsUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Adds items to a shipment with idempotency enabled (2026-01 onwards)

  #### Query

  ```graphql
  mutation inventoryShipmentAddItems($id: ID!, $lineItems: [InventoryShipmentLineItemInput!]!, $idempotencyKey: String!) {
    inventoryShipmentAddItems(id: $id, lineItems: $lineItems) @idempotent(key: $idempotencyKey) {
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
    "id": "gid://shopify/InventoryShipment/787965984",
    "lineItems": [
      {
        "inventoryItemId": "gid://shopify/InventoryItem/113711323",
        "quantity": 1
      }
    ],
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
  "query": "mutation inventoryShipmentAddItems($id: ID!, $lineItems: [InventoryShipmentLineItemInput!]!, $idempotencyKey: String!) { inventoryShipmentAddItems(id: $id, lineItems: $lineItems) @idempotent(key: $idempotencyKey) { userErrors { field message code } inventoryShipment { id status } } }",
   "variables": {
      "id": "gid://shopify/InventoryShipment/787965984",
      "lineItems": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/113711323",
          "quantity": 1
        }
      ],
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
    mutation inventoryShipmentAddItems($id: ID!, $lineItems: [InventoryShipmentLineItemInput!]!, $idempotencyKey: String!) {
      inventoryShipmentAddItems(id: $id, lineItems: $lineItems) @idempotent(key: $idempotencyKey) {
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
          "id": "gid://shopify/InventoryShipment/787965984",
          "lineItems": [
              {
                  "inventoryItemId": "gid://shopify/InventoryItem/113711323",
                  "quantity": 1
              }
          ],
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
    mutation inventoryShipmentAddItems($id: ID!, $lineItems: [InventoryShipmentLineItemInput!]!, $idempotencyKey: String!) {
      inventoryShipmentAddItems(id: $id, lineItems: $lineItems) @idempotent(key: $idempotencyKey) {
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
    "id": "gid://shopify/InventoryShipment/787965984",
    "lineItems": [
      {
        "inventoryItemId": "gid://shopify/InventoryItem/113711323",
        "quantity": 1
      }
    ],
    "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation inventoryShipmentAddItems($id: ID!, $lineItems: [InventoryShipmentLineItemInput!]!, $idempotencyKey: String!) {
        inventoryShipmentAddItems(id: $id, lineItems: $lineItems) @idempotent(key: $idempotencyKey) {
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
          "id": "gid://shopify/InventoryShipment/787965984",
          "lineItems": [
              {
                  "inventoryItemId": "gid://shopify/InventoryItem/113711323",
                  "quantity": 1
              }
          ],
          "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation inventoryShipmentAddItems($id: ID!, $lineItems: [InventoryShipmentLineItemInput!]!, $idempotencyKey: String!) {
    inventoryShipmentAddItems(id: $id, lineItems: $lineItems) @idempotent(key: $idempotencyKey) {
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
    "id": "gid://shopify/InventoryShipment/787965984",
    "lineItems": [
      {
        "inventoryItemId": "gid://shopify/InventoryItem/113711323",
        "quantity": 1
      }
    ],
    "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000"
  }'
  ```

  #### Response

  ```json
  {
    "inventoryShipmentAddItems": {
      "userErrors": [],
      "inventoryShipment": {
        "id": "gid://shopify/InventoryShipment/787965984",
        "status": "DRAFT"
      }
    }
  }
  ```

* ### inventoryShipmentAddItems reference
