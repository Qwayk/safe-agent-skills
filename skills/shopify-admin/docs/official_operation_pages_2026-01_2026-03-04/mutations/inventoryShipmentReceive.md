---
title: inventoryShipmentReceive - GraphQL Admin
description: >-
  Receive an inventory shipment.


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
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventoryShipmentReceive
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventoryShipmentReceive.md
---

# inventory​Shipment​Receive

mutation

Requires `write_inventory_shipments_received_items` access scope. Also: The user must have permission to manage inventory.

Receive an inventory shipment.

***

**Caution:** As of 2026-01, this mutation supports an optional idempotency key using the \<code>@idempotent\</code> directive. As of 2026-04, the idempotency key is required and must be provided using the \<code>@idempotent\</code> directive. For more information, see the \<a href="https://shopify.dev/docs/api/usage/idempotent-requests">idempotency documentation\</a>.

***

## Arguments

* bulk​Receive​Action

  [Inventory​Shipment​Receive​Line​Item​Reason](https://shopify.dev/docs/api/admin-graphql/latest/enums/InventoryShipmentReceiveLineItemReason)

  The bulk receive action for the inventory shipment.

* date​Received

  [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

  The date the inventory shipment was initially received.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the inventory shipment to receive.

* line​Items

  [\[Inventory​Shipment​Receive​Item​Input!\]](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/InventoryShipmentReceiveItemInput)

  The list of receive line items for the inventory shipment.

***

## Inventory​Shipment​Receive​Payload returns

* inventory​Shipment

  [Inventory​Shipment](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryShipment)

  The inventory shipment with received items.

* user​Errors

  [\[Inventory​Shipment​Receive​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryShipmentReceiveUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Receives a shipment

  #### Query

  ```graphql
  mutation inventoryShipmentReceive($id: ID!, $lineItems: [InventoryShipmentReceiveItemInput!]) {
    inventoryShipmentReceive(id: $id, lineItems: $lineItems) {
      userErrors {
        field
        message
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
    "id": "gid://shopify/InventoryShipment/340744744",
    "lineItems": [
      {
        "shipmentLineItemId": "gid://shopify/InventoryShipmentLineItem/925690278",
        "quantity": 10,
        "reason": "ACCEPTED"
      }
    ]
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation inventoryShipmentReceive($id: ID!, $lineItems: [InventoryShipmentReceiveItemInput!]) { inventoryShipmentReceive(id: $id, lineItems: $lineItems) { userErrors { field message } inventoryShipment { id status } } }",
   "variables": {
      "id": "gid://shopify/InventoryShipment/340744744",
      "lineItems": [
        {
          "shipmentLineItemId": "gid://shopify/InventoryShipmentLineItem/925690278",
          "quantity": 10,
          "reason": "ACCEPTED"
        }
      ]
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
    mutation inventoryShipmentReceive($id: ID!, $lineItems: [InventoryShipmentReceiveItemInput!]) {
      inventoryShipmentReceive(id: $id, lineItems: $lineItems) {
        userErrors {
          field
          message
        }
        inventoryShipment {
          id
          status
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/InventoryShipment/340744744",
          "lineItems": [
              {
                  "shipmentLineItemId": "gid://shopify/InventoryShipmentLineItem/925690278",
                  "quantity": 10,
                  "reason": "ACCEPTED"
              }
          ]
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
    mutation inventoryShipmentReceive($id: ID!, $lineItems: [InventoryShipmentReceiveItemInput!]) {
      inventoryShipmentReceive(id: $id, lineItems: $lineItems) {
        userErrors {
          field
          message
        }
        inventoryShipment {
          id
          status
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/InventoryShipment/340744744",
    "lineItems": [
      {
        "shipmentLineItemId": "gid://shopify/InventoryShipmentLineItem/925690278",
        "quantity": 10,
        "reason": "ACCEPTED"
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation inventoryShipmentReceive($id: ID!, $lineItems: [InventoryShipmentReceiveItemInput!]) {
        inventoryShipmentReceive(id: $id, lineItems: $lineItems) {
          userErrors {
            field
            message
          }
          inventoryShipment {
            id
            status
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/InventoryShipment/340744744",
          "lineItems": [
              {
                  "shipmentLineItemId": "gid://shopify/InventoryShipmentLineItem/925690278",
                  "quantity": 10,
                  "reason": "ACCEPTED"
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation inventoryShipmentReceive($id: ID!, $lineItems: [InventoryShipmentReceiveItemInput!]) {
    inventoryShipmentReceive(id: $id, lineItems: $lineItems) {
      userErrors {
        field
        message
      }
      inventoryShipment {
        id
        status
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/InventoryShipment/340744744",
    "lineItems": [
      {
        "shipmentLineItemId": "gid://shopify/InventoryShipmentLineItem/925690278",
        "quantity": 10,
        "reason": "ACCEPTED"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "inventoryShipmentReceive": {
      "userErrors": [],
      "inventoryShipment": {
        "id": "gid://shopify/InventoryShipment/340744744",
        "status": "RECEIVED"
      }
    }
  }
  ```

* ### Receives a shipment with idempotency enabled (2026-01 onwards)

  #### Query

  ```graphql
  mutation inventoryShipmentReceive($id: ID!, $lineItems: [InventoryShipmentReceiveItemInput!], $idempotencyKey: String!) {
    inventoryShipmentReceive(id: $id, lineItems: $lineItems) @idempotent(key: $idempotencyKey) {
      userErrors {
        field
        message
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
    "id": "gid://shopify/InventoryShipment/340744744",
    "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000",
    "lineItems": [
      {
        "shipmentLineItemId": "gid://shopify/InventoryShipmentLineItem/925690278",
        "quantity": 10,
        "reason": "ACCEPTED"
      }
    ]
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation inventoryShipmentReceive($id: ID!, $lineItems: [InventoryShipmentReceiveItemInput!], $idempotencyKey: String!) { inventoryShipmentReceive(id: $id, lineItems: $lineItems) @idempotent(key: $idempotencyKey) { userErrors { field message } inventoryShipment { id status } } }",
   "variables": {
      "id": "gid://shopify/InventoryShipment/340744744",
      "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000",
      "lineItems": [
        {
          "shipmentLineItemId": "gid://shopify/InventoryShipmentLineItem/925690278",
          "quantity": 10,
          "reason": "ACCEPTED"
        }
      ]
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
    mutation inventoryShipmentReceive($id: ID!, $lineItems: [InventoryShipmentReceiveItemInput!], $idempotencyKey: String!) {
      inventoryShipmentReceive(id: $id, lineItems: $lineItems) @idempotent(key: $idempotencyKey) {
        userErrors {
          field
          message
        }
        inventoryShipment {
          id
          status
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/InventoryShipment/340744744",
          "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000",
          "lineItems": [
              {
                  "shipmentLineItemId": "gid://shopify/InventoryShipmentLineItem/925690278",
                  "quantity": 10,
                  "reason": "ACCEPTED"
              }
          ]
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
    mutation inventoryShipmentReceive($id: ID!, $lineItems: [InventoryShipmentReceiveItemInput!], $idempotencyKey: String!) {
      inventoryShipmentReceive(id: $id, lineItems: $lineItems) @idempotent(key: $idempotencyKey) {
        userErrors {
          field
          message
        }
        inventoryShipment {
          id
          status
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/InventoryShipment/340744744",
    "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000",
    "lineItems": [
      {
        "shipmentLineItemId": "gid://shopify/InventoryShipmentLineItem/925690278",
        "quantity": 10,
        "reason": "ACCEPTED"
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation inventoryShipmentReceive($id: ID!, $lineItems: [InventoryShipmentReceiveItemInput!], $idempotencyKey: String!) {
        inventoryShipmentReceive(id: $id, lineItems: $lineItems) @idempotent(key: $idempotencyKey) {
          userErrors {
            field
            message
          }
          inventoryShipment {
            id
            status
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/InventoryShipment/340744744",
          "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000",
          "lineItems": [
              {
                  "shipmentLineItemId": "gid://shopify/InventoryShipmentLineItem/925690278",
                  "quantity": 10,
                  "reason": "ACCEPTED"
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation inventoryShipmentReceive($id: ID!, $lineItems: [InventoryShipmentReceiveItemInput!], $idempotencyKey: String!) {
    inventoryShipmentReceive(id: $id, lineItems: $lineItems) @idempotent(key: $idempotencyKey) {
      userErrors {
        field
        message
      }
      inventoryShipment {
        id
        status
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/InventoryShipment/340744744",
    "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000",
    "lineItems": [
      {
        "shipmentLineItemId": "gid://shopify/InventoryShipmentLineItem/925690278",
        "quantity": 10,
        "reason": "ACCEPTED"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "inventoryShipmentReceive": {
      "userErrors": [],
      "inventoryShipment": {
        "id": "gid://shopify/InventoryShipment/340744744",
        "status": "RECEIVED"
      }
    }
  }
  ```

* ### inventoryShipmentReceive reference
