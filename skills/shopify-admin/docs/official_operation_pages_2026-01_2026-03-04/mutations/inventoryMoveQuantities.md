---
title: inventoryMoveQuantities - GraphQL Admin
description: >-
  Moves inventory quantities for a single inventory item between different
  states at a single location. Use this mutation to reallocate inventory across
  quantity states without moving it between locations.


  Each change specifies the quantity to move, the source state and location, and
  the destination state and location. The mutation returns an
  [`InventoryAdjustmentGroup`](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryAdjustmentGroup)
  that tracks all changes made in a single operation, providing an audit trail
  with the reason and reference document URI.


  > Caution:

  > As of version `2026-01`, this mutation supports an optional idempotency key
  using the `@idempotent` directive.

  > As of version `2026-04`, the idempotency key is required and must be
  provided using the `@idempotent` directive.

  > For more information, see the [idempotency
  documentation](https://shopify.dev/docs/api/usage/idempotent-requests).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventoryMoveQuantities
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventoryMoveQuantities.md
---

# inventory​Move​Quantities

mutation

Requires `write_inventory` access scope. Also: The user must have a permission to move an inventory.

Moves inventory quantities for a single inventory item between different states at a single location. Use this mutation to reallocate inventory across quantity states without moving it between locations.

Each change specifies the quantity to move, the source state and location, and the destination state and location. The mutation returns an [`InventoryAdjustmentGroup`](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryAdjustmentGroup) that tracks all changes made in a single operation, providing an audit trail with the reason and reference document URI.

***

**Caution:** As of version \<code>2026-01\</code>, this mutation supports an optional idempotency key using the \<code>@idempotent\</code> directive. As of version \<code>2026-04\</code>, the idempotency key is required and must be provided using the \<code>@idempotent\</code> directive. For more information, see the \<a href="https://shopify.dev/docs/api/usage/idempotent-requests">idempotency documentation\</a>.

***

## Arguments

* input

  [Inventory​Move​Quantities​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/InventoryMoveQuantitiesInput)

  required

  The information required to move inventory quantities.

***

## Inventory​Move​Quantities​Payload returns

* inventory​Adjustment​Group

  [Inventory​Adjustment​Group](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryAdjustmentGroup)

  The group of changes made by the operation.

* user​Errors

  [\[Inventory​Move​Quantities​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryMoveQuantitiesUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Move 10 items from available to reserved with idempotency enabled and compare-and-swap disabled (2026-01 onwards)

  #### Query

  ```graphql
  mutation inventoryMoveQuantities($input: InventoryMoveQuantitiesInput!, $quantityNames: [String!], $idempotencyKey: String!) {
    inventoryMoveQuantities(input: $input) @idempotent(key: $idempotencyKey) {
      userErrors {
        field
        message
        code
      }
      inventoryAdjustmentGroup {
        createdAt
        reason
        referenceDocumentUri
        changes(quantityNames: $quantityNames) {
          name
          delta
          ledgerDocumentUri
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "reason": "damaged",
      "referenceDocumentUri": "logistics://some.warehouse/take/2026-02-23T13:14:15Z",
      "changes": [
        {
          "quantity": 10,
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "from": {
            "locationId": "gid://shopify/Location/124656943",
            "name": "available",
            "ledgerDocumentUri": null,
            "changeFromQuantity": null
          },
          "to": {
            "locationId": "gid://shopify/Location/124656943",
            "name": "reserved",
            "ledgerDocumentUri": "logistics://toronto.warehouse/work-orders/2026-02-04/2",
            "changeFromQuantity": null
          }
        }
      ]
    },
    "quantityNames": [
      "committed",
      "reserved",
      "safety_stock",
      "quality_control",
      "damaged",
      "available",
      "on_hand",
      "incoming"
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
  "query": "mutation inventoryMoveQuantities($input: InventoryMoveQuantitiesInput!, $quantityNames: [String!], $idempotencyKey: String!) { inventoryMoveQuantities(input: $input) @idempotent(key: $idempotencyKey) { userErrors { field message code } inventoryAdjustmentGroup { createdAt reason referenceDocumentUri changes(quantityNames: $quantityNames) { name delta ledgerDocumentUri } } } }",
   "variables": {
      "input": {
        "reason": "damaged",
        "referenceDocumentUri": "logistics://some.warehouse/take/2026-02-23T13:14:15Z",
        "changes": [
          {
            "quantity": 10,
            "inventoryItemId": "gid://shopify/InventoryItem/30322695",
            "from": {
              "locationId": "gid://shopify/Location/124656943",
              "name": "available",
              "ledgerDocumentUri": null,
              "changeFromQuantity": null
            },
            "to": {
              "locationId": "gid://shopify/Location/124656943",
              "name": "reserved",
              "ledgerDocumentUri": "logistics://toronto.warehouse/work-orders/2026-02-04/2",
              "changeFromQuantity": null
            }
          }
        ]
      },
      "quantityNames": [
        "committed",
        "reserved",
        "safety_stock",
        "quality_control",
        "damaged",
        "available",
        "on_hand",
        "incoming"
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
    mutation inventoryMoveQuantities($input: InventoryMoveQuantitiesInput!, $quantityNames: [String!], $idempotencyKey: String!) {
      inventoryMoveQuantities(input: $input) @idempotent(key: $idempotencyKey) {
        userErrors {
          field
          message
          code
        }
        inventoryAdjustmentGroup {
          createdAt
          reason
          referenceDocumentUri
          changes(quantityNames: $quantityNames) {
            name
            delta
            ledgerDocumentUri
          }
        }
      }
    }`,
    {
      variables: {
          "input": {
              "reason": "damaged",
              "referenceDocumentUri": "logistics://some.warehouse/take/2026-02-23T13:14:15Z",
              "changes": [
                  {
                      "quantity": 10,
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "from": {
                          "locationId": "gid://shopify/Location/124656943",
                          "name": "available",
                          "ledgerDocumentUri": null,
                          "changeFromQuantity": null
                      },
                      "to": {
                          "locationId": "gid://shopify/Location/124656943",
                          "name": "reserved",
                          "ledgerDocumentUri": "logistics://toronto.warehouse/work-orders/2026-02-04/2",
                          "changeFromQuantity": null
                      }
                  }
              ]
          },
          "quantityNames": [
              "committed",
              "reserved",
              "safety_stock",
              "quality_control",
              "damaged",
              "available",
              "on_hand",
              "incoming"
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
    mutation inventoryMoveQuantities($input: InventoryMoveQuantitiesInput!, $quantityNames: [String!], $idempotencyKey: String!) {
      inventoryMoveQuantities(input: $input) @idempotent(key: $idempotencyKey) {
        userErrors {
          field
          message
          code
        }
        inventoryAdjustmentGroup {
          createdAt
          reason
          referenceDocumentUri
          changes(quantityNames: $quantityNames) {
            name
            delta
            ledgerDocumentUri
          }
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "reason": "damaged",
      "referenceDocumentUri": "logistics://some.warehouse/take/2026-02-23T13:14:15Z",
      "changes": [
        {
          "quantity": 10,
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "from": {
            "locationId": "gid://shopify/Location/124656943",
            "name": "available",
            "ledgerDocumentUri": null,
            "changeFromQuantity": null
          },
          "to": {
            "locationId": "gid://shopify/Location/124656943",
            "name": "reserved",
            "ledgerDocumentUri": "logistics://toronto.warehouse/work-orders/2026-02-04/2",
            "changeFromQuantity": null
          }
        }
      ]
    },
    "quantityNames": [
      "committed",
      "reserved",
      "safety_stock",
      "quality_control",
      "damaged",
      "available",
      "on_hand",
      "incoming"
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
      "query": `mutation inventoryMoveQuantities($input: InventoryMoveQuantitiesInput!, $quantityNames: [String!], $idempotencyKey: String!) {
        inventoryMoveQuantities(input: $input) @idempotent(key: $idempotencyKey) {
          userErrors {
            field
            message
            code
          }
          inventoryAdjustmentGroup {
            createdAt
            reason
            referenceDocumentUri
            changes(quantityNames: $quantityNames) {
              name
              delta
              ledgerDocumentUri
            }
          }
        }
      }`,
      "variables": {
          "input": {
              "reason": "damaged",
              "referenceDocumentUri": "logistics://some.warehouse/take/2026-02-23T13:14:15Z",
              "changes": [
                  {
                      "quantity": 10,
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "from": {
                          "locationId": "gid://shopify/Location/124656943",
                          "name": "available",
                          "ledgerDocumentUri": null,
                          "changeFromQuantity": null
                      },
                      "to": {
                          "locationId": "gid://shopify/Location/124656943",
                          "name": "reserved",
                          "ledgerDocumentUri": "logistics://toronto.warehouse/work-orders/2026-02-04/2",
                          "changeFromQuantity": null
                      }
                  }
              ]
          },
          "quantityNames": [
              "committed",
              "reserved",
              "safety_stock",
              "quality_control",
              "damaged",
              "available",
              "on_hand",
              "incoming"
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
  'mutation inventoryMoveQuantities($input: InventoryMoveQuantitiesInput!, $quantityNames: [String!], $idempotencyKey: String!) {
    inventoryMoveQuantities(input: $input) @idempotent(key: $idempotencyKey) {
      userErrors {
        field
        message
        code
      }
      inventoryAdjustmentGroup {
        createdAt
        reason
        referenceDocumentUri
        changes(quantityNames: $quantityNames) {
          name
          delta
          ledgerDocumentUri
        }
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "reason": "damaged",
      "referenceDocumentUri": "logistics://some.warehouse/take/2026-02-23T13:14:15Z",
      "changes": [
        {
          "quantity": 10,
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "from": {
            "locationId": "gid://shopify/Location/124656943",
            "name": "available",
            "ledgerDocumentUri": null,
            "changeFromQuantity": null
          },
          "to": {
            "locationId": "gid://shopify/Location/124656943",
            "name": "reserved",
            "ledgerDocumentUri": "logistics://toronto.warehouse/work-orders/2026-02-04/2",
            "changeFromQuantity": null
          }
        }
      ]
    },
    "quantityNames": [
      "committed",
      "reserved",
      "safety_stock",
      "quality_control",
      "damaged",
      "available",
      "on_hand",
      "incoming"
    ],
    "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000"
  }'
  ```

  #### Response

  ```json
  {
    "inventoryMoveQuantities": {
      "userErrors": [],
      "inventoryAdjustmentGroup": {
        "createdAt": "2026-01-21T21:23:45Z",
        "reason": "Damaged",
        "referenceDocumentUri": "logistics://some.warehouse/take/2026-02-23T13:14:15Z",
        "changes": [
          {
            "name": "available",
            "delta": -10,
            "ledgerDocumentUri": null
          },
          {
            "name": "reserved",
            "delta": 10,
            "ledgerDocumentUri": "logistics://toronto.warehouse/work-orders/2026-02-04/2"
          }
        ]
      }
    }
  }
  ```

* ### Move 10 items from available to reserved with idempotency enabled and compare-and-swap enabled (2026-01 onwards)

  #### Query

  ```graphql
  mutation inventoryMoveQuantities($input: InventoryMoveQuantitiesInput!, $quantityNames: [String!], $idempotencyKey: String!) {
    inventoryMoveQuantities(input: $input) @idempotent(key: $idempotencyKey) {
      userErrors {
        field
        message
        code
      }
      inventoryAdjustmentGroup {
        createdAt
        reason
        referenceDocumentUri
        changes(quantityNames: $quantityNames) {
          name
          delta
          ledgerDocumentUri
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "reason": "damaged",
      "referenceDocumentUri": "logistics://some.warehouse/take/2026-02-23T13:14:15Z",
      "changes": [
        {
          "quantity": 10,
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "from": {
            "locationId": "gid://shopify/Location/124656943",
            "name": "available",
            "ledgerDocumentUri": null,
            "changeFromQuantity": 1
          },
          "to": {
            "locationId": "gid://shopify/Location/124656943",
            "name": "reserved",
            "ledgerDocumentUri": "logistics://toronto.warehouse/work-orders/2026-02-04/2",
            "changeFromQuantity": 440
          }
        }
      ]
    },
    "quantityNames": [
      "committed",
      "reserved",
      "safety_stock",
      "quality_control",
      "damaged",
      "available",
      "on_hand",
      "incoming"
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
  "query": "mutation inventoryMoveQuantities($input: InventoryMoveQuantitiesInput!, $quantityNames: [String!], $idempotencyKey: String!) { inventoryMoveQuantities(input: $input) @idempotent(key: $idempotencyKey) { userErrors { field message code } inventoryAdjustmentGroup { createdAt reason referenceDocumentUri changes(quantityNames: $quantityNames) { name delta ledgerDocumentUri } } } }",
   "variables": {
      "input": {
        "reason": "damaged",
        "referenceDocumentUri": "logistics://some.warehouse/take/2026-02-23T13:14:15Z",
        "changes": [
          {
            "quantity": 10,
            "inventoryItemId": "gid://shopify/InventoryItem/30322695",
            "from": {
              "locationId": "gid://shopify/Location/124656943",
              "name": "available",
              "ledgerDocumentUri": null,
              "changeFromQuantity": 1
            },
            "to": {
              "locationId": "gid://shopify/Location/124656943",
              "name": "reserved",
              "ledgerDocumentUri": "logistics://toronto.warehouse/work-orders/2026-02-04/2",
              "changeFromQuantity": 440
            }
          }
        ]
      },
      "quantityNames": [
        "committed",
        "reserved",
        "safety_stock",
        "quality_control",
        "damaged",
        "available",
        "on_hand",
        "incoming"
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
    mutation inventoryMoveQuantities($input: InventoryMoveQuantitiesInput!, $quantityNames: [String!], $idempotencyKey: String!) {
      inventoryMoveQuantities(input: $input) @idempotent(key: $idempotencyKey) {
        userErrors {
          field
          message
          code
        }
        inventoryAdjustmentGroup {
          createdAt
          reason
          referenceDocumentUri
          changes(quantityNames: $quantityNames) {
            name
            delta
            ledgerDocumentUri
          }
        }
      }
    }`,
    {
      variables: {
          "input": {
              "reason": "damaged",
              "referenceDocumentUri": "logistics://some.warehouse/take/2026-02-23T13:14:15Z",
              "changes": [
                  {
                      "quantity": 10,
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "from": {
                          "locationId": "gid://shopify/Location/124656943",
                          "name": "available",
                          "ledgerDocumentUri": null,
                          "changeFromQuantity": 1
                      },
                      "to": {
                          "locationId": "gid://shopify/Location/124656943",
                          "name": "reserved",
                          "ledgerDocumentUri": "logistics://toronto.warehouse/work-orders/2026-02-04/2",
                          "changeFromQuantity": 440
                      }
                  }
              ]
          },
          "quantityNames": [
              "committed",
              "reserved",
              "safety_stock",
              "quality_control",
              "damaged",
              "available",
              "on_hand",
              "incoming"
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
    mutation inventoryMoveQuantities($input: InventoryMoveQuantitiesInput!, $quantityNames: [String!], $idempotencyKey: String!) {
      inventoryMoveQuantities(input: $input) @idempotent(key: $idempotencyKey) {
        userErrors {
          field
          message
          code
        }
        inventoryAdjustmentGroup {
          createdAt
          reason
          referenceDocumentUri
          changes(quantityNames: $quantityNames) {
            name
            delta
            ledgerDocumentUri
          }
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "reason": "damaged",
      "referenceDocumentUri": "logistics://some.warehouse/take/2026-02-23T13:14:15Z",
      "changes": [
        {
          "quantity": 10,
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "from": {
            "locationId": "gid://shopify/Location/124656943",
            "name": "available",
            "ledgerDocumentUri": null,
            "changeFromQuantity": 1
          },
          "to": {
            "locationId": "gid://shopify/Location/124656943",
            "name": "reserved",
            "ledgerDocumentUri": "logistics://toronto.warehouse/work-orders/2026-02-04/2",
            "changeFromQuantity": 440
          }
        }
      ]
    },
    "quantityNames": [
      "committed",
      "reserved",
      "safety_stock",
      "quality_control",
      "damaged",
      "available",
      "on_hand",
      "incoming"
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
      "query": `mutation inventoryMoveQuantities($input: InventoryMoveQuantitiesInput!, $quantityNames: [String!], $idempotencyKey: String!) {
        inventoryMoveQuantities(input: $input) @idempotent(key: $idempotencyKey) {
          userErrors {
            field
            message
            code
          }
          inventoryAdjustmentGroup {
            createdAt
            reason
            referenceDocumentUri
            changes(quantityNames: $quantityNames) {
              name
              delta
              ledgerDocumentUri
            }
          }
        }
      }`,
      "variables": {
          "input": {
              "reason": "damaged",
              "referenceDocumentUri": "logistics://some.warehouse/take/2026-02-23T13:14:15Z",
              "changes": [
                  {
                      "quantity": 10,
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "from": {
                          "locationId": "gid://shopify/Location/124656943",
                          "name": "available",
                          "ledgerDocumentUri": null,
                          "changeFromQuantity": 1
                      },
                      "to": {
                          "locationId": "gid://shopify/Location/124656943",
                          "name": "reserved",
                          "ledgerDocumentUri": "logistics://toronto.warehouse/work-orders/2026-02-04/2",
                          "changeFromQuantity": 440
                      }
                  }
              ]
          },
          "quantityNames": [
              "committed",
              "reserved",
              "safety_stock",
              "quality_control",
              "damaged",
              "available",
              "on_hand",
              "incoming"
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
  'mutation inventoryMoveQuantities($input: InventoryMoveQuantitiesInput!, $quantityNames: [String!], $idempotencyKey: String!) {
    inventoryMoveQuantities(input: $input) @idempotent(key: $idempotencyKey) {
      userErrors {
        field
        message
        code
      }
      inventoryAdjustmentGroup {
        createdAt
        reason
        referenceDocumentUri
        changes(quantityNames: $quantityNames) {
          name
          delta
          ledgerDocumentUri
        }
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "reason": "damaged",
      "referenceDocumentUri": "logistics://some.warehouse/take/2026-02-23T13:14:15Z",
      "changes": [
        {
          "quantity": 10,
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "from": {
            "locationId": "gid://shopify/Location/124656943",
            "name": "available",
            "ledgerDocumentUri": null,
            "changeFromQuantity": 1
          },
          "to": {
            "locationId": "gid://shopify/Location/124656943",
            "name": "reserved",
            "ledgerDocumentUri": "logistics://toronto.warehouse/work-orders/2026-02-04/2",
            "changeFromQuantity": 440
          }
        }
      ]
    },
    "quantityNames": [
      "committed",
      "reserved",
      "safety_stock",
      "quality_control",
      "damaged",
      "available",
      "on_hand",
      "incoming"
    ],
    "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000"
  }'
  ```

  #### Response

  ```json
  {
    "inventoryMoveQuantities": {
      "userErrors": [],
      "inventoryAdjustmentGroup": {
        "createdAt": "2026-01-21T21:23:47Z",
        "reason": "Damaged",
        "referenceDocumentUri": "logistics://some.warehouse/take/2026-02-23T13:14:15Z",
        "changes": [
          {
            "name": "available",
            "delta": -10,
            "ledgerDocumentUri": null
          },
          {
            "name": "reserved",
            "delta": 10,
            "ledgerDocumentUri": "logistics://toronto.warehouse/work-orders/2026-02-04/2"
          }
        ]
      }
    }
  }
  ```

* ### Move 10 items from available to reserved, with reason damaged.

  #### Query

  ```graphql
  mutation inventoryMoveQuantities($input: InventoryMoveQuantitiesInput!, $quantityNames: [String!]) {
    inventoryMoveQuantities(input: $input) {
      userErrors {
        field
        message
        code
      }
      inventoryAdjustmentGroup {
        createdAt
        reason
        referenceDocumentUri
        changes(quantityNames: $quantityNames) {
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
      "reason": "damaged",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "changes": [
        {
          "quantity": 10,
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "from": {
            "locationId": "gid://shopify/Location/124656943",
            "name": "available",
            "ledgerDocumentUri": null
          },
          "to": {
            "locationId": "gid://shopify/Location/124656943",
            "name": "reserved",
            "ledgerDocumentUri": "logistics://toronto.warehouse/work-orders/2023-01-04/2"
          }
        }
      ]
    },
    "quantityNames": [
      "committed",
      "reserved",
      "safety_stock",
      "quality_control",
      "damaged",
      "available",
      "on_hand",
      "incoming"
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
  "query": "mutation inventoryMoveQuantities($input: InventoryMoveQuantitiesInput!, $quantityNames: [String!]) { inventoryMoveQuantities(input: $input) { userErrors { field message code } inventoryAdjustmentGroup { createdAt reason referenceDocumentUri changes(quantityNames: $quantityNames) { name delta } } } }",
   "variables": {
      "input": {
        "reason": "damaged",
        "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
        "changes": [
          {
            "quantity": 10,
            "inventoryItemId": "gid://shopify/InventoryItem/30322695",
            "from": {
              "locationId": "gid://shopify/Location/124656943",
              "name": "available",
              "ledgerDocumentUri": null
            },
            "to": {
              "locationId": "gid://shopify/Location/124656943",
              "name": "reserved",
              "ledgerDocumentUri": "logistics://toronto.warehouse/work-orders/2023-01-04/2"
            }
          }
        ]
      },
      "quantityNames": [
        "committed",
        "reserved",
        "safety_stock",
        "quality_control",
        "damaged",
        "available",
        "on_hand",
        "incoming"
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
    mutation inventoryMoveQuantities($input: InventoryMoveQuantitiesInput!, $quantityNames: [String!]) {
      inventoryMoveQuantities(input: $input) {
        userErrors {
          field
          message
          code
        }
        inventoryAdjustmentGroup {
          createdAt
          reason
          referenceDocumentUri
          changes(quantityNames: $quantityNames) {
            name
            delta
          }
        }
      }
    }`,
    {
      variables: {
          "input": {
              "reason": "damaged",
              "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
              "changes": [
                  {
                      "quantity": 10,
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "from": {
                          "locationId": "gid://shopify/Location/124656943",
                          "name": "available",
                          "ledgerDocumentUri": null
                      },
                      "to": {
                          "locationId": "gid://shopify/Location/124656943",
                          "name": "reserved",
                          "ledgerDocumentUri": "logistics://toronto.warehouse/work-orders/2023-01-04/2"
                      }
                  }
              ]
          },
          "quantityNames": [
              "committed",
              "reserved",
              "safety_stock",
              "quality_control",
              "damaged",
              "available",
              "on_hand",
              "incoming"
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
    mutation inventoryMoveQuantities($input: InventoryMoveQuantitiesInput!, $quantityNames: [String!]) {
      inventoryMoveQuantities(input: $input) {
        userErrors {
          field
          message
          code
        }
        inventoryAdjustmentGroup {
          createdAt
          reason
          referenceDocumentUri
          changes(quantityNames: $quantityNames) {
            name
            delta
          }
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "reason": "damaged",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "changes": [
        {
          "quantity": 10,
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "from": {
            "locationId": "gid://shopify/Location/124656943",
            "name": "available",
            "ledgerDocumentUri": null
          },
          "to": {
            "locationId": "gid://shopify/Location/124656943",
            "name": "reserved",
            "ledgerDocumentUri": "logistics://toronto.warehouse/work-orders/2023-01-04/2"
          }
        }
      ]
    },
    "quantityNames": [
      "committed",
      "reserved",
      "safety_stock",
      "quality_control",
      "damaged",
      "available",
      "on_hand",
      "incoming"
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation inventoryMoveQuantities($input: InventoryMoveQuantitiesInput!, $quantityNames: [String!]) {
        inventoryMoveQuantities(input: $input) {
          userErrors {
            field
            message
            code
          }
          inventoryAdjustmentGroup {
            createdAt
            reason
            referenceDocumentUri
            changes(quantityNames: $quantityNames) {
              name
              delta
            }
          }
        }
      }`,
      "variables": {
          "input": {
              "reason": "damaged",
              "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
              "changes": [
                  {
                      "quantity": 10,
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "from": {
                          "locationId": "gid://shopify/Location/124656943",
                          "name": "available",
                          "ledgerDocumentUri": null
                      },
                      "to": {
                          "locationId": "gid://shopify/Location/124656943",
                          "name": "reserved",
                          "ledgerDocumentUri": "logistics://toronto.warehouse/work-orders/2023-01-04/2"
                      }
                  }
              ]
          },
          "quantityNames": [
              "committed",
              "reserved",
              "safety_stock",
              "quality_control",
              "damaged",
              "available",
              "on_hand",
              "incoming"
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation inventoryMoveQuantities($input: InventoryMoveQuantitiesInput!, $quantityNames: [String!]) {
    inventoryMoveQuantities(input: $input) {
      userErrors {
        field
        message
        code
      }
      inventoryAdjustmentGroup {
        createdAt
        reason
        referenceDocumentUri
        changes(quantityNames: $quantityNames) {
          name
          delta
        }
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "reason": "damaged",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "changes": [
        {
          "quantity": 10,
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "from": {
            "locationId": "gid://shopify/Location/124656943",
            "name": "available",
            "ledgerDocumentUri": null
          },
          "to": {
            "locationId": "gid://shopify/Location/124656943",
            "name": "reserved",
            "ledgerDocumentUri": "logistics://toronto.warehouse/work-orders/2023-01-04/2"
          }
        }
      ]
    },
    "quantityNames": [
      "committed",
      "reserved",
      "safety_stock",
      "quality_control",
      "damaged",
      "available",
      "on_hand",
      "incoming"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "inventoryMoveQuantities": {
      "userErrors": [],
      "inventoryAdjustmentGroup": {
        "createdAt": "2024-09-12T01:06:28Z",
        "reason": "Damaged",
        "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
        "changes": [
          {
            "name": "available",
            "delta": -10
          },
          {
            "name": "reserved",
            "delta": 10
          }
        ]
      }
    }
  }
  ```

* ### Move 10 items from available to reserved, with reason damaged.

  #### Query

  ```graphql
  mutation inventoryMoveQuantities($input: InventoryMoveQuantitiesInput!, $quantityNames: [String!]) {
    inventoryMoveQuantities(input: $input) {
      userErrors {
        field
        message
        code
      }
      inventoryAdjustmentGroup {
        createdAt
        reason
        referenceDocumentUri
        changes(quantityNames: $quantityNames) {
          name
          delta
          ledgerDocumentUri
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "reason": "damaged",
      "referenceDocumentUri": "logistics://some.warehouse/take/2025-10-23T13:14:15Z",
      "changes": [
        {
          "quantity": 10,
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "from": {
            "locationId": "gid://shopify/Location/124656943",
            "name": "available",
            "ledgerDocumentUri": null
          },
          "to": {
            "locationId": "gid://shopify/Location/124656943",
            "name": "reserved",
            "ledgerDocumentUri": "logistics://toronto.warehouse/work-orders/2025-10-04/2"
          }
        }
      ]
    },
    "quantityNames": [
      "committed",
      "reserved",
      "safety_stock",
      "quality_control",
      "damaged",
      "available",
      "on_hand",
      "incoming"
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
  "query": "mutation inventoryMoveQuantities($input: InventoryMoveQuantitiesInput!, $quantityNames: [String!]) { inventoryMoveQuantities(input: $input) { userErrors { field message code } inventoryAdjustmentGroup { createdAt reason referenceDocumentUri changes(quantityNames: $quantityNames) { name delta ledgerDocumentUri } } } }",
   "variables": {
      "input": {
        "reason": "damaged",
        "referenceDocumentUri": "logistics://some.warehouse/take/2025-10-23T13:14:15Z",
        "changes": [
          {
            "quantity": 10,
            "inventoryItemId": "gid://shopify/InventoryItem/30322695",
            "from": {
              "locationId": "gid://shopify/Location/124656943",
              "name": "available",
              "ledgerDocumentUri": null
            },
            "to": {
              "locationId": "gid://shopify/Location/124656943",
              "name": "reserved",
              "ledgerDocumentUri": "logistics://toronto.warehouse/work-orders/2025-10-04/2"
            }
          }
        ]
      },
      "quantityNames": [
        "committed",
        "reserved",
        "safety_stock",
        "quality_control",
        "damaged",
        "available",
        "on_hand",
        "incoming"
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
    mutation inventoryMoveQuantities($input: InventoryMoveQuantitiesInput!, $quantityNames: [String!]) {
      inventoryMoveQuantities(input: $input) {
        userErrors {
          field
          message
          code
        }
        inventoryAdjustmentGroup {
          createdAt
          reason
          referenceDocumentUri
          changes(quantityNames: $quantityNames) {
            name
            delta
            ledgerDocumentUri
          }
        }
      }
    }`,
    {
      variables: {
          "input": {
              "reason": "damaged",
              "referenceDocumentUri": "logistics://some.warehouse/take/2025-10-23T13:14:15Z",
              "changes": [
                  {
                      "quantity": 10,
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "from": {
                          "locationId": "gid://shopify/Location/124656943",
                          "name": "available",
                          "ledgerDocumentUri": null
                      },
                      "to": {
                          "locationId": "gid://shopify/Location/124656943",
                          "name": "reserved",
                          "ledgerDocumentUri": "logistics://toronto.warehouse/work-orders/2025-10-04/2"
                      }
                  }
              ]
          },
          "quantityNames": [
              "committed",
              "reserved",
              "safety_stock",
              "quality_control",
              "damaged",
              "available",
              "on_hand",
              "incoming"
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
    mutation inventoryMoveQuantities($input: InventoryMoveQuantitiesInput!, $quantityNames: [String!]) {
      inventoryMoveQuantities(input: $input) {
        userErrors {
          field
          message
          code
        }
        inventoryAdjustmentGroup {
          createdAt
          reason
          referenceDocumentUri
          changes(quantityNames: $quantityNames) {
            name
            delta
            ledgerDocumentUri
          }
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "reason": "damaged",
      "referenceDocumentUri": "logistics://some.warehouse/take/2025-10-23T13:14:15Z",
      "changes": [
        {
          "quantity": 10,
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "from": {
            "locationId": "gid://shopify/Location/124656943",
            "name": "available",
            "ledgerDocumentUri": null
          },
          "to": {
            "locationId": "gid://shopify/Location/124656943",
            "name": "reserved",
            "ledgerDocumentUri": "logistics://toronto.warehouse/work-orders/2025-10-04/2"
          }
        }
      ]
    },
    "quantityNames": [
      "committed",
      "reserved",
      "safety_stock",
      "quality_control",
      "damaged",
      "available",
      "on_hand",
      "incoming"
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation inventoryMoveQuantities($input: InventoryMoveQuantitiesInput!, $quantityNames: [String!]) {
        inventoryMoveQuantities(input: $input) {
          userErrors {
            field
            message
            code
          }
          inventoryAdjustmentGroup {
            createdAt
            reason
            referenceDocumentUri
            changes(quantityNames: $quantityNames) {
              name
              delta
              ledgerDocumentUri
            }
          }
        }
      }`,
      "variables": {
          "input": {
              "reason": "damaged",
              "referenceDocumentUri": "logistics://some.warehouse/take/2025-10-23T13:14:15Z",
              "changes": [
                  {
                      "quantity": 10,
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "from": {
                          "locationId": "gid://shopify/Location/124656943",
                          "name": "available",
                          "ledgerDocumentUri": null
                      },
                      "to": {
                          "locationId": "gid://shopify/Location/124656943",
                          "name": "reserved",
                          "ledgerDocumentUri": "logistics://toronto.warehouse/work-orders/2025-10-04/2"
                      }
                  }
              ]
          },
          "quantityNames": [
              "committed",
              "reserved",
              "safety_stock",
              "quality_control",
              "damaged",
              "available",
              "on_hand",
              "incoming"
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation inventoryMoveQuantities($input: InventoryMoveQuantitiesInput!, $quantityNames: [String!]) {
    inventoryMoveQuantities(input: $input) {
      userErrors {
        field
        message
        code
      }
      inventoryAdjustmentGroup {
        createdAt
        reason
        referenceDocumentUri
        changes(quantityNames: $quantityNames) {
          name
          delta
          ledgerDocumentUri
        }
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "reason": "damaged",
      "referenceDocumentUri": "logistics://some.warehouse/take/2025-10-23T13:14:15Z",
      "changes": [
        {
          "quantity": 10,
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "from": {
            "locationId": "gid://shopify/Location/124656943",
            "name": "available",
            "ledgerDocumentUri": null
          },
          "to": {
            "locationId": "gid://shopify/Location/124656943",
            "name": "reserved",
            "ledgerDocumentUri": "logistics://toronto.warehouse/work-orders/2025-10-04/2"
          }
        }
      ]
    },
    "quantityNames": [
      "committed",
      "reserved",
      "safety_stock",
      "quality_control",
      "damaged",
      "available",
      "on_hand",
      "incoming"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "inventoryMoveQuantities": {
      "userErrors": [],
      "inventoryAdjustmentGroup": {
        "createdAt": "2026-01-21T21:23:47Z",
        "reason": "Damaged",
        "referenceDocumentUri": "logistics://some.warehouse/take/2025-10-23T13:14:15Z",
        "changes": [
          {
            "name": "available",
            "delta": -10,
            "ledgerDocumentUri": null
          },
          {
            "name": "reserved",
            "delta": 10,
            "ledgerDocumentUri": "logistics://toronto.warehouse/work-orders/2025-10-04/2"
          }
        ]
      }
    }
  }
  ```

* ### inventoryMoveQuantities reference
