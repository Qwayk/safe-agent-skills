---
title: inventorySetOnHandQuantities - GraphQL Admin
description: >-
  Sets an inventory item's on-hand quantities to specific absolute values at
  designated locations. The mutation takes a reason for tracking purposes and a
  reference document URI for audit trails.


  Returns an
  [`InventoryAdjustmentGroup`](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryAdjustmentGroup)
  that tracks all changes made in this operation, including the delta values
  calculated from the previous quantities.


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
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventorySetOnHandQuantities
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventorySetOnHandQuantities.md
---

# inventory​Set​On​Hand​Quantities

mutation

Requires `write_inventory` access scope. Also: The user must have a permission to update an inventory.

Deprecated. Use [inventorySetQuantities](https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventorySetQuantities) to set on\_hand or available quantites instead.

Sets an inventory item's on-hand quantities to specific absolute values at designated locations. The mutation takes a reason for tracking purposes and a reference document URI for audit trails.

Returns an [`InventoryAdjustmentGroup`](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryAdjustmentGroup) that tracks all changes made in this operation, including the delta values calculated from the previous quantities.

***

**Caution:** As of 2026-01, this mutation supports an optional idempotency key using the \<code>@idempotent\</code> directive. As of 2026-04, the idempotency key is required and must be provided using the \<code>@idempotent\</code> directive. For more information, see the \<a href="https://shopify.dev/docs/api/usage/idempotent-requests">idempotency documentation\</a>.

***

## Arguments

* input

  [Inventory​Set​On​Hand​Quantities​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/InventorySetOnHandQuantitiesInput)

  required

  The information required to set inventory on hand quantities.

***

## Inventory​Set​On​Hand​Quantities​Payload returns

* inventory​Adjustment​Group

  [Inventory​Adjustment​Group](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryAdjustmentGroup)

  The group of changes made by the operation.

* user​Errors

  [\[Inventory​Set​On​Hand​Quantities​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventorySetOnHandQuantitiesUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Adjust on\_hand quantity for 2 items with idempotency enabled and compare-and-swap disabled (2026-01 onwards)

  #### Query

  ```graphql
  mutation inventorySetOnHandQuantities($input: InventorySetOnHandQuantitiesInput!, $idempotencyKey: String!) {
    inventorySetOnHandQuantities(input: $input) @idempotent(key: $idempotencyKey) {
      userErrors {
        field
        message
      }
      inventoryAdjustmentGroup {
        createdAt
        reason
        referenceDocumentUri
        changes {
          name
          delta
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "setQuantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 42,
          "changeFromQuantity": null
        },
        {
          "inventoryItemId": "gid://shopify/InventoryItem/113711323",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 13,
          "changeFromQuantity": null
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
  "query": "mutation inventorySetOnHandQuantities($input: InventorySetOnHandQuantitiesInput!, $idempotencyKey: String!) { inventorySetOnHandQuantities(input: $input) @idempotent(key: $idempotencyKey) { userErrors { field message } inventoryAdjustmentGroup { createdAt reason referenceDocumentUri changes { name delta } } } }",
   "variables": {
      "input": {
        "reason": "correction",
        "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
        "setQuantities": [
          {
            "inventoryItemId": "gid://shopify/InventoryItem/30322695",
            "locationId": "gid://shopify/Location/124656943",
            "quantity": 42,
            "changeFromQuantity": null
          },
          {
            "inventoryItemId": "gid://shopify/InventoryItem/113711323",
            "locationId": "gid://shopify/Location/124656943",
            "quantity": 13,
            "changeFromQuantity": null
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
    mutation inventorySetOnHandQuantities($input: InventorySetOnHandQuantitiesInput!, $idempotencyKey: String!) {
      inventorySetOnHandQuantities(input: $input) @idempotent(key: $idempotencyKey) {
        userErrors {
          field
          message
        }
        inventoryAdjustmentGroup {
          createdAt
          reason
          referenceDocumentUri
          changes {
            name
            delta
          }
        }
      }
    }`,
    {
      variables: {
          "input": {
              "reason": "correction",
              "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
              "setQuantities": [
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 42,
                      "changeFromQuantity": null
                  },
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/113711323",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 13,
                      "changeFromQuantity": null
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
    mutation inventorySetOnHandQuantities($input: InventorySetOnHandQuantitiesInput!, $idempotencyKey: String!) {
      inventorySetOnHandQuantities(input: $input) @idempotent(key: $idempotencyKey) {
        userErrors {
          field
          message
        }
        inventoryAdjustmentGroup {
          createdAt
          reason
          referenceDocumentUri
          changes {
            name
            delta
          }
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "setQuantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 42,
          "changeFromQuantity": null
        },
        {
          "inventoryItemId": "gid://shopify/InventoryItem/113711323",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 13,
          "changeFromQuantity": null
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
      "query": `mutation inventorySetOnHandQuantities($input: InventorySetOnHandQuantitiesInput!, $idempotencyKey: String!) {
        inventorySetOnHandQuantities(input: $input) @idempotent(key: $idempotencyKey) {
          userErrors {
            field
            message
          }
          inventoryAdjustmentGroup {
            createdAt
            reason
            referenceDocumentUri
            changes {
              name
              delta
            }
          }
        }
      }`,
      "variables": {
          "input": {
              "reason": "correction",
              "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
              "setQuantities": [
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 42,
                      "changeFromQuantity": null
                  },
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/113711323",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 13,
                      "changeFromQuantity": null
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
  'mutation inventorySetOnHandQuantities($input: InventorySetOnHandQuantitiesInput!, $idempotencyKey: String!) {
    inventorySetOnHandQuantities(input: $input) @idempotent(key: $idempotencyKey) {
      userErrors {
        field
        message
      }
      inventoryAdjustmentGroup {
        createdAt
        reason
        referenceDocumentUri
        changes {
          name
          delta
        }
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "setQuantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 42,
          "changeFromQuantity": null
        },
        {
          "inventoryItemId": "gid://shopify/InventoryItem/113711323",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 13,
          "changeFromQuantity": null
        }
      ]
    },
    "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000"
  }'
  ```

  #### Response

  ```json
  {
    "inventorySetOnHandQuantities": {
      "userErrors": [],
      "inventoryAdjustmentGroup": {
        "createdAt": "2026-01-16T01:36:50Z",
        "reason": "Inventory correction",
        "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
        "changes": [
          {
            "name": "available",
            "delta": -399
          },
          {
            "name": "available",
            "delta": -413
          },
          {
            "name": "on_hand",
            "delta": -399
          },
          {
            "name": "on_hand",
            "delta": -413
          }
        ]
      }
    }
  }
  ```

* ### Adjust on\_hand quantity for 2 items with idempotency enabled and compare-and-swap enabled (2026-01 onwards)

  #### Query

  ```graphql
  mutation inventorySetOnHandQuantities($input: InventorySetOnHandQuantitiesInput!, $idempotencyKey: String!) {
    inventorySetOnHandQuantities(input: $input) @idempotent(key: $idempotencyKey) {
      userErrors {
        field
        message
      }
      inventoryAdjustmentGroup {
        createdAt
        reason
        referenceDocumentUri
        changes {
          name
          delta
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "setQuantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 42,
          "changeFromQuantity": 441
        },
        {
          "inventoryItemId": "gid://shopify/InventoryItem/113711323",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 13,
          "changeFromQuantity": 426
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
  "query": "mutation inventorySetOnHandQuantities($input: InventorySetOnHandQuantitiesInput!, $idempotencyKey: String!) { inventorySetOnHandQuantities(input: $input) @idempotent(key: $idempotencyKey) { userErrors { field message } inventoryAdjustmentGroup { createdAt reason referenceDocumentUri changes { name delta } } } }",
   "variables": {
      "input": {
        "reason": "correction",
        "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
        "setQuantities": [
          {
            "inventoryItemId": "gid://shopify/InventoryItem/30322695",
            "locationId": "gid://shopify/Location/124656943",
            "quantity": 42,
            "changeFromQuantity": 441
          },
          {
            "inventoryItemId": "gid://shopify/InventoryItem/113711323",
            "locationId": "gid://shopify/Location/124656943",
            "quantity": 13,
            "changeFromQuantity": 426
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
    mutation inventorySetOnHandQuantities($input: InventorySetOnHandQuantitiesInput!, $idempotencyKey: String!) {
      inventorySetOnHandQuantities(input: $input) @idempotent(key: $idempotencyKey) {
        userErrors {
          field
          message
        }
        inventoryAdjustmentGroup {
          createdAt
          reason
          referenceDocumentUri
          changes {
            name
            delta
          }
        }
      }
    }`,
    {
      variables: {
          "input": {
              "reason": "correction",
              "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
              "setQuantities": [
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 42,
                      "changeFromQuantity": 441
                  },
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/113711323",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 13,
                      "changeFromQuantity": 426
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
    mutation inventorySetOnHandQuantities($input: InventorySetOnHandQuantitiesInput!, $idempotencyKey: String!) {
      inventorySetOnHandQuantities(input: $input) @idempotent(key: $idempotencyKey) {
        userErrors {
          field
          message
        }
        inventoryAdjustmentGroup {
          createdAt
          reason
          referenceDocumentUri
          changes {
            name
            delta
          }
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "setQuantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 42,
          "changeFromQuantity": 441
        },
        {
          "inventoryItemId": "gid://shopify/InventoryItem/113711323",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 13,
          "changeFromQuantity": 426
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
      "query": `mutation inventorySetOnHandQuantities($input: InventorySetOnHandQuantitiesInput!, $idempotencyKey: String!) {
        inventorySetOnHandQuantities(input: $input) @idempotent(key: $idempotencyKey) {
          userErrors {
            field
            message
          }
          inventoryAdjustmentGroup {
            createdAt
            reason
            referenceDocumentUri
            changes {
              name
              delta
            }
          }
        }
      }`,
      "variables": {
          "input": {
              "reason": "correction",
              "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
              "setQuantities": [
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 42,
                      "changeFromQuantity": 441
                  },
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/113711323",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 13,
                      "changeFromQuantity": 426
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
  'mutation inventorySetOnHandQuantities($input: InventorySetOnHandQuantitiesInput!, $idempotencyKey: String!) {
    inventorySetOnHandQuantities(input: $input) @idempotent(key: $idempotencyKey) {
      userErrors {
        field
        message
      }
      inventoryAdjustmentGroup {
        createdAt
        reason
        referenceDocumentUri
        changes {
          name
          delta
        }
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "setQuantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 42,
          "changeFromQuantity": 441
        },
        {
          "inventoryItemId": "gid://shopify/InventoryItem/113711323",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 13,
          "changeFromQuantity": 426
        }
      ]
    },
    "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000"
  }'
  ```

  #### Response

  ```json
  {
    "inventorySetOnHandQuantities": {
      "userErrors": [],
      "inventoryAdjustmentGroup": {
        "createdAt": "2026-01-16T01:36:49Z",
        "reason": "Inventory correction",
        "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
        "changes": [
          {
            "name": "available",
            "delta": -399
          },
          {
            "name": "available",
            "delta": -413
          },
          {
            "name": "on_hand",
            "delta": -399
          },
          {
            "name": "on_hand",
            "delta": -413
          }
        ]
      }
    }
  }
  ```

* ### Adjust on\_hand quantity for 2 items, with reason 'correction'.

  #### Query

  ```graphql
  mutation inventorySetOnHandQuantities($input: InventorySetOnHandQuantitiesInput!) {
    inventorySetOnHandQuantities(input: $input) {
      userErrors {
        field
        message
      }
      inventoryAdjustmentGroup {
        createdAt
        reason
        referenceDocumentUri
        changes {
          name
          delta
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "setQuantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 42
        },
        {
          "inventoryItemId": "gid://shopify/InventoryItem/113711323",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 13
        }
      ]
    }
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation inventorySetOnHandQuantities($input: InventorySetOnHandQuantitiesInput!) { inventorySetOnHandQuantities(input: $input) { userErrors { field message } inventoryAdjustmentGroup { createdAt reason referenceDocumentUri changes { name delta } } } }",
   "variables": {
      "input": {
        "reason": "correction",
        "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
        "setQuantities": [
          {
            "inventoryItemId": "gid://shopify/InventoryItem/30322695",
            "locationId": "gid://shopify/Location/124656943",
            "quantity": 42
          },
          {
            "inventoryItemId": "gid://shopify/InventoryItem/113711323",
            "locationId": "gid://shopify/Location/124656943",
            "quantity": 13
          }
        ]
      }
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
    mutation inventorySetOnHandQuantities($input: InventorySetOnHandQuantitiesInput!) {
      inventorySetOnHandQuantities(input: $input) {
        userErrors {
          field
          message
        }
        inventoryAdjustmentGroup {
          createdAt
          reason
          referenceDocumentUri
          changes {
            name
            delta
          }
        }
      }
    }`,
    {
      variables: {
          "input": {
              "reason": "correction",
              "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
              "setQuantities": [
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 42
                  },
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/113711323",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 13
                  }
              ]
          }
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
    mutation inventorySetOnHandQuantities($input: InventorySetOnHandQuantitiesInput!) {
      inventorySetOnHandQuantities(input: $input) {
        userErrors {
          field
          message
        }
        inventoryAdjustmentGroup {
          createdAt
          reason
          referenceDocumentUri
          changes {
            name
            delta
          }
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "setQuantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 42
        },
        {
          "inventoryItemId": "gid://shopify/InventoryItem/113711323",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 13
        }
      ]
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation inventorySetOnHandQuantities($input: InventorySetOnHandQuantitiesInput!) {
        inventorySetOnHandQuantities(input: $input) {
          userErrors {
            field
            message
          }
          inventoryAdjustmentGroup {
            createdAt
            reason
            referenceDocumentUri
            changes {
              name
              delta
            }
          }
        }
      }`,
      "variables": {
          "input": {
              "reason": "correction",
              "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
              "setQuantities": [
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 42
                  },
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/113711323",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 13
                  }
              ]
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation inventorySetOnHandQuantities($input: InventorySetOnHandQuantitiesInput!) {
    inventorySetOnHandQuantities(input: $input) {
      userErrors {
        field
        message
      }
      inventoryAdjustmentGroup {
        createdAt
        reason
        referenceDocumentUri
        changes {
          name
          delta
        }
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "setQuantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 42
        },
        {
          "inventoryItemId": "gid://shopify/InventoryItem/113711323",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 13
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "inventorySetOnHandQuantities": {
      "userErrors": [],
      "inventoryAdjustmentGroup": {
        "createdAt": "2024-09-12T01:05:46Z",
        "reason": "Inventory correction",
        "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
        "changes": [
          {
            "name": "available",
            "delta": 31
          },
          {
            "name": "available",
            "delta": 12
          },
          {
            "name": "on_hand",
            "delta": 31
          },
          {
            "name": "on_hand",
            "delta": 12
          }
        ]
      }
    }
  }
  ```

* ### Adjust on\_hand quantity for 2 items, with reason 'correction'.

  #### Query

  ```graphql
  mutation inventorySetOnHandQuantities($input: InventorySetOnHandQuantitiesInput!) {
    inventorySetOnHandQuantities(input: $input) {
      userErrors {
        field
        message
      }
      inventoryAdjustmentGroup {
        createdAt
        reason
        referenceDocumentUri
        changes {
          name
          delta
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "setQuantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 42
        },
        {
          "inventoryItemId": "gid://shopify/InventoryItem/113711323",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 13
        }
      ]
    }
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation inventorySetOnHandQuantities($input: InventorySetOnHandQuantitiesInput!) { inventorySetOnHandQuantities(input: $input) { userErrors { field message } inventoryAdjustmentGroup { createdAt reason referenceDocumentUri changes { name delta } } } }",
   "variables": {
      "input": {
        "reason": "correction",
        "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
        "setQuantities": [
          {
            "inventoryItemId": "gid://shopify/InventoryItem/30322695",
            "locationId": "gid://shopify/Location/124656943",
            "quantity": 42
          },
          {
            "inventoryItemId": "gid://shopify/InventoryItem/113711323",
            "locationId": "gid://shopify/Location/124656943",
            "quantity": 13
          }
        ]
      }
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
    mutation inventorySetOnHandQuantities($input: InventorySetOnHandQuantitiesInput!) {
      inventorySetOnHandQuantities(input: $input) {
        userErrors {
          field
          message
        }
        inventoryAdjustmentGroup {
          createdAt
          reason
          referenceDocumentUri
          changes {
            name
            delta
          }
        }
      }
    }`,
    {
      variables: {
          "input": {
              "reason": "correction",
              "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
              "setQuantities": [
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 42
                  },
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/113711323",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 13
                  }
              ]
          }
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
    mutation inventorySetOnHandQuantities($input: InventorySetOnHandQuantitiesInput!) {
      inventorySetOnHandQuantities(input: $input) {
        userErrors {
          field
          message
        }
        inventoryAdjustmentGroup {
          createdAt
          reason
          referenceDocumentUri
          changes {
            name
            delta
          }
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "setQuantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 42
        },
        {
          "inventoryItemId": "gid://shopify/InventoryItem/113711323",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 13
        }
      ]
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation inventorySetOnHandQuantities($input: InventorySetOnHandQuantitiesInput!) {
        inventorySetOnHandQuantities(input: $input) {
          userErrors {
            field
            message
          }
          inventoryAdjustmentGroup {
            createdAt
            reason
            referenceDocumentUri
            changes {
              name
              delta
            }
          }
        }
      }`,
      "variables": {
          "input": {
              "reason": "correction",
              "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
              "setQuantities": [
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 42
                  },
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/113711323",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 13
                  }
              ]
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation inventorySetOnHandQuantities($input: InventorySetOnHandQuantitiesInput!) {
    inventorySetOnHandQuantities(input: $input) {
      userErrors {
        field
        message
      }
      inventoryAdjustmentGroup {
        createdAt
        reason
        referenceDocumentUri
        changes {
          name
          delta
        }
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "setQuantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 42
        },
        {
          "inventoryItemId": "gid://shopify/InventoryItem/113711323",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 13
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "inventorySetOnHandQuantities": {
      "userErrors": [],
      "inventoryAdjustmentGroup": {
        "createdAt": "2026-01-16T01:36:50Z",
        "reason": "Inventory correction",
        "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
        "changes": [
          {
            "name": "available",
            "delta": -399
          },
          {
            "name": "available",
            "delta": -413
          },
          {
            "name": "on_hand",
            "delta": -399
          },
          {
            "name": "on_hand",
            "delta": -413
          }
        ]
      }
    }
  }
  ```

* ### inventorySetOnHandQuantities reference
