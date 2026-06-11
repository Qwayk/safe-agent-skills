---
title: inventorySetQuantities - GraphQL Admin
description: >-
  Set quantities of specified name using absolute values. This mutation supports
  compare-and-set functionality to handle

  concurrent requests properly. If `ignoreCompareQuantity` is not set to true,

  the mutation will only update the quantity if the persisted quantity matches
  the `compareQuantity` value.

  If the `compareQuantity` value does not match the persisted value, the
  mutation will return an error. In order to opt out

  of the `compareQuantity` check, the `ignoreCompareQuantity` argument can be
  set to true.


  > Note:

  > Only use this mutation if calling on behalf of a system that acts as the
  main reference for inventory quantities,

  > otherwise please consider using the
  [inventoryAdjustQuantities](https://shopify.dev/api/admin-graphql/latest/mutations/inventoryAdjustQuantities)
  mutation.

  >

  >

  > Opting out of the `compareQuantity` check can lead to inaccurate inventory
  quantities if multiple requests are made concurrently.

  > It is recommended to always include the `compareQuantity` value to ensure
  the accuracy of the inventory quantities and to opt out

  > of the check using `ignoreCompareQuantity` only when necessary.


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
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventorySetQuantities
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventorySetQuantities.md
---

# inventory​Set​Quantities

mutation

Requires `write_inventory` access scope. Also: The user must have a permission to update an inventory.

Set quantities of specified name using absolute values. This mutation supports compare-and-set functionality to handle concurrent requests properly. If `ignoreCompareQuantity` is not set to true, the mutation will only update the quantity if the persisted quantity matches the `compareQuantity` value. If the `compareQuantity` value does not match the persisted value, the mutation will return an error. In order to opt out of the `compareQuantity` check, the `ignoreCompareQuantity` argument can be set to true.

***

**Note:** Only use this mutation if calling on behalf of a system that acts as the main reference for inventory quantities, otherwise please consider using the \<a href="https://shopify.dev/api/admin-graphql/latest/mutations/inventoryAdjustQuantities">inventoryAdjustQuantities\</a> mutation.\</p> \<p>Opting out of the \<code>\<span class="PreventFireFoxApplyingGapToWBR">compare\<wbr/>Quantity\</span>\</code> check can lead to inaccurate inventory quantities if multiple requests are made concurrently. It is recommended to always include the \<code>\<span class="PreventFireFoxApplyingGapToWBR">compare\<wbr/>Quantity\</span>\</code> value to ensure the accuracy of the inventory quantities and to opt out of the check using \<code>\<span class="PreventFireFoxApplyingGapToWBR">ignore\<wbr/>Compare\<wbr/>Quantity\</span>\</code> only when necessary.

***

***

**Caution:** As of 2026-01, this mutation supports an optional idempotency key using the \<code>@idempotent\</code> directive. As of 2026-04, the idempotency key is required and must be provided using the \<code>@idempotent\</code> directive. For more information, see the \<a href="https://shopify.dev/docs/api/usage/idempotent-requests">idempotency documentation\</a>.

***

## Arguments

* input

  [Inventory​Set​Quantities​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/InventorySetQuantitiesInput)

  required

  The information required to set inventory quantities.

***

## Inventory​Set​Quantities​Payload returns

* inventory​Adjustment​Group

  [Inventory​Adjustment​Group](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryAdjustmentGroup)

  The group of changes made by the operation.

* user​Errors

  [\[Inventory​Set​Quantities​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventorySetQuantitiesUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Sets the inventory level for an inventory item at a location

  #### Query

  ```graphql
  mutation InventorySet($input: InventorySetQuantitiesInput!) {
    inventorySetQuantities(input: $input) {
      inventoryAdjustmentGroup {
        createdAt
        reason
        referenceDocumentUri
        changes {
          name
          delta
        }
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
    "input": {
      "name": "available",
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "quantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 11,
          "compareQuantity": 1
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
  "query": "mutation InventorySet($input: InventorySetQuantitiesInput!) { inventorySetQuantities(input: $input) { inventoryAdjustmentGroup { createdAt reason referenceDocumentUri changes { name delta } } userErrors { field message } } }",
   "variables": {
      "input": {
        "name": "available",
        "reason": "correction",
        "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
        "quantities": [
          {
            "inventoryItemId": "gid://shopify/InventoryItem/30322695",
            "locationId": "gid://shopify/Location/124656943",
            "quantity": 11,
            "compareQuantity": 1
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
    mutation InventorySet($input: InventorySetQuantitiesInput!) {
      inventorySetQuantities(input: $input) {
        inventoryAdjustmentGroup {
          createdAt
          reason
          referenceDocumentUri
          changes {
            name
            delta
          }
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "input": {
              "name": "available",
              "reason": "correction",
              "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
              "quantities": [
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 11,
                      "compareQuantity": 1
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
    mutation InventorySet($input: InventorySetQuantitiesInput!) {
      inventorySetQuantities(input: $input) {
        inventoryAdjustmentGroup {
          createdAt
          reason
          referenceDocumentUri
          changes {
            name
            delta
          }
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "name": "available",
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "quantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 11,
          "compareQuantity": 1
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
      "query": `mutation InventorySet($input: InventorySetQuantitiesInput!) {
        inventorySetQuantities(input: $input) {
          inventoryAdjustmentGroup {
            createdAt
            reason
            referenceDocumentUri
            changes {
              name
              delta
            }
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "name": "available",
              "reason": "correction",
              "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
              "quantities": [
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 11,
                      "compareQuantity": 1
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
  'mutation InventorySet($input: InventorySetQuantitiesInput!) {
    inventorySetQuantities(input: $input) {
      inventoryAdjustmentGroup {
        createdAt
        reason
        referenceDocumentUri
        changes {
          name
          delta
        }
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "name": "available",
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "quantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 11,
          "compareQuantity": 1
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "inventorySetQuantities": {
      "inventoryAdjustmentGroup": {
        "createdAt": "2024-11-07T22:03:12Z",
        "reason": "Inventory correction",
        "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
        "changes": [
          {
            "name": "available",
            "delta": 10
          },
          {
            "name": "on_hand",
            "delta": 10
          }
        ]
      },
      "userErrors": []
    }
  }
  ```

* ### Sets the inventory level for an inventory item at a location with compare-and-swap disabled (prior to 2026-04)

  #### Query

  ```graphql
  mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
    inventorySetQuantities(input: $input) {
      inventoryAdjustmentGroup {
        reason
        referenceDocumentUri
        changes {
          name
          delta
          quantityAfterChange
        }
      }
      userErrors {
        code
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "name": "available",
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "ignoreCompareQuantity": true,
      "quantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 42
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
  "query": "mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) { inventorySetQuantities(input: $input) { inventoryAdjustmentGroup { reason referenceDocumentUri changes { name delta quantityAfterChange } } userErrors { code field message } } }",
   "variables": {
      "input": {
        "name": "available",
        "reason": "correction",
        "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
        "ignoreCompareQuantity": true,
        "quantities": [
          {
            "inventoryItemId": "gid://shopify/InventoryItem/30322695",
            "locationId": "gid://shopify/Location/124656943",
            "quantity": 42
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
    mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
      inventorySetQuantities(input: $input) {
        inventoryAdjustmentGroup {
          reason
          referenceDocumentUri
          changes {
            name
            delta
            quantityAfterChange
          }
        }
        userErrors {
          code
          field
          message
        }
      }
    }`,
    {
      variables: {
          "input": {
              "name": "available",
              "reason": "correction",
              "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
              "ignoreCompareQuantity": true,
              "quantities": [
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 42
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
    mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
      inventorySetQuantities(input: $input) {
        inventoryAdjustmentGroup {
          reason
          referenceDocumentUri
          changes {
            name
            delta
            quantityAfterChange
          }
        }
        userErrors {
          code
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "name": "available",
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "ignoreCompareQuantity": true,
      "quantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 42
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
      "query": `mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
        inventorySetQuantities(input: $input) {
          inventoryAdjustmentGroup {
            reason
            referenceDocumentUri
            changes {
              name
              delta
              quantityAfterChange
            }
          }
          userErrors {
            code
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "name": "available",
              "reason": "correction",
              "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
              "ignoreCompareQuantity": true,
              "quantities": [
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 42
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
  'mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
    inventorySetQuantities(input: $input) {
      inventoryAdjustmentGroup {
        reason
        referenceDocumentUri
        changes {
          name
          delta
          quantityAfterChange
        }
      }
      userErrors {
        code
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "name": "available",
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "ignoreCompareQuantity": true,
      "quantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 42
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "inventorySetQuantities": {
      "inventoryAdjustmentGroup": {
        "reason": "Inventory correction",
        "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
        "changes": [
          {
            "name": "available",
            "delta": 41,
            "quantityAfterChange": null
          },
          {
            "name": "on_hand",
            "delta": 41,
            "quantityAfterChange": null
          }
        ]
      },
      "userErrors": []
    }
  }
  ```

* ### Sets the inventory level for an inventory item at a location with compare-and-swap enabled (prior to 2026-04)

  #### Query

  ```graphql
  mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
    inventorySetQuantities(input: $input) {
      inventoryAdjustmentGroup {
        createdAt
        reason
        referenceDocumentUri
        changes {
          name
          delta
          quantityAfterChange
        }
      }
      userErrors {
        code
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "name": "available",
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "quantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 11,
          "compareQuantity": 1
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
  "query": "mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) { inventorySetQuantities(input: $input) { inventoryAdjustmentGroup { createdAt reason referenceDocumentUri changes { name delta quantityAfterChange } } userErrors { code field message } } }",
   "variables": {
      "input": {
        "name": "available",
        "reason": "correction",
        "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
        "quantities": [
          {
            "inventoryItemId": "gid://shopify/InventoryItem/30322695",
            "locationId": "gid://shopify/Location/124656943",
            "quantity": 11,
            "compareQuantity": 1
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
    mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
      inventorySetQuantities(input: $input) {
        inventoryAdjustmentGroup {
          createdAt
          reason
          referenceDocumentUri
          changes {
            name
            delta
            quantityAfterChange
          }
        }
        userErrors {
          code
          field
          message
        }
      }
    }`,
    {
      variables: {
          "input": {
              "name": "available",
              "reason": "correction",
              "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
              "quantities": [
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 11,
                      "compareQuantity": 1
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
    mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
      inventorySetQuantities(input: $input) {
        inventoryAdjustmentGroup {
          createdAt
          reason
          referenceDocumentUri
          changes {
            name
            delta
            quantityAfterChange
          }
        }
        userErrors {
          code
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "name": "available",
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "quantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 11,
          "compareQuantity": 1
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
      "query": `mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
        inventorySetQuantities(input: $input) {
          inventoryAdjustmentGroup {
            createdAt
            reason
            referenceDocumentUri
            changes {
              name
              delta
              quantityAfterChange
            }
          }
          userErrors {
            code
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "name": "available",
              "reason": "correction",
              "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
              "quantities": [
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 11,
                      "compareQuantity": 1
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
  'mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
    inventorySetQuantities(input: $input) {
      inventoryAdjustmentGroup {
        createdAt
        reason
        referenceDocumentUri
        changes {
          name
          delta
          quantityAfterChange
        }
      }
      userErrors {
        code
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "name": "available",
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "quantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 11,
          "compareQuantity": 1
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "inventorySetQuantities": {
      "inventoryAdjustmentGroup": {
        "createdAt": "2026-01-16T01:44:41Z",
        "reason": "Inventory correction",
        "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
        "changes": [
          {
            "name": "available",
            "delta": 10,
            "quantityAfterChange": null
          },
          {
            "name": "on_hand",
            "delta": 10,
            "quantityAfterChange": null
          }
        ]
      },
      "userErrors": []
    }
  }
  ```

* ### Sets the inventory level for an inventory item at a location with idempotency enabled and compare-and-swap disabled (2026-01 onwards)

  #### Query

  ```graphql
  mutation inventorySetQuantities($input: InventorySetQuantitiesInput!, $idempotencyKey: String!) {
    inventorySetQuantities(input: $input) @idempotent(key: $idempotencyKey) {
      inventoryAdjustmentGroup {
        reason
        referenceDocumentUri
        changes {
          name
          delta
          quantityAfterChange
        }
      }
      userErrors {
        code
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "name": "available",
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "quantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 42,
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
  "query": "mutation inventorySetQuantities($input: InventorySetQuantitiesInput!, $idempotencyKey: String!) { inventorySetQuantities(input: $input) @idempotent(key: $idempotencyKey) { inventoryAdjustmentGroup { reason referenceDocumentUri changes { name delta quantityAfterChange } } userErrors { code field message } } }",
   "variables": {
      "input": {
        "name": "available",
        "reason": "correction",
        "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
        "quantities": [
          {
            "inventoryItemId": "gid://shopify/InventoryItem/30322695",
            "locationId": "gid://shopify/Location/124656943",
            "quantity": 42,
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
    mutation inventorySetQuantities($input: InventorySetQuantitiesInput!, $idempotencyKey: String!) {
      inventorySetQuantities(input: $input) @idempotent(key: $idempotencyKey) {
        inventoryAdjustmentGroup {
          reason
          referenceDocumentUri
          changes {
            name
            delta
            quantityAfterChange
          }
        }
        userErrors {
          code
          field
          message
        }
      }
    }`,
    {
      variables: {
          "input": {
              "name": "available",
              "reason": "correction",
              "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
              "quantities": [
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 42,
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
    mutation inventorySetQuantities($input: InventorySetQuantitiesInput!, $idempotencyKey: String!) {
      inventorySetQuantities(input: $input) @idempotent(key: $idempotencyKey) {
        inventoryAdjustmentGroup {
          reason
          referenceDocumentUri
          changes {
            name
            delta
            quantityAfterChange
          }
        }
        userErrors {
          code
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "name": "available",
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "quantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 42,
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
      "query": `mutation inventorySetQuantities($input: InventorySetQuantitiesInput!, $idempotencyKey: String!) {
        inventorySetQuantities(input: $input) @idempotent(key: $idempotencyKey) {
          inventoryAdjustmentGroup {
            reason
            referenceDocumentUri
            changes {
              name
              delta
              quantityAfterChange
            }
          }
          userErrors {
            code
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "name": "available",
              "reason": "correction",
              "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
              "quantities": [
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 42,
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
  'mutation inventorySetQuantities($input: InventorySetQuantitiesInput!, $idempotencyKey: String!) {
    inventorySetQuantities(input: $input) @idempotent(key: $idempotencyKey) {
      inventoryAdjustmentGroup {
        reason
        referenceDocumentUri
        changes {
          name
          delta
          quantityAfterChange
        }
      }
      userErrors {
        code
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "name": "available",
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "quantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 42,
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
    "inventorySetQuantities": {
      "inventoryAdjustmentGroup": {
        "reason": "Inventory correction",
        "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
        "changes": [
          {
            "name": "available",
            "delta": 41,
            "quantityAfterChange": null
          },
          {
            "name": "on_hand",
            "delta": 41,
            "quantityAfterChange": null
          }
        ]
      },
      "userErrors": []
    }
  }
  ```

* ### Sets the inventory level for an inventory item at a location with idempotency enabled and compare-and-swap enabled (2026-01 onwards)

  #### Query

  ```graphql
  mutation inventorySetQuantities($input: InventorySetQuantitiesInput!, $idempotencyKey: String!) {
    inventorySetQuantities(input: $input) @idempotent(key: $idempotencyKey) {
      inventoryAdjustmentGroup {
        reason
        referenceDocumentUri
        changes {
          name
          delta
          quantityAfterChange
        }
      }
      userErrors {
        code
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "name": "available",
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "quantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 42,
          "changeFromQuantity": 1
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
  "query": "mutation inventorySetQuantities($input: InventorySetQuantitiesInput!, $idempotencyKey: String!) { inventorySetQuantities(input: $input) @idempotent(key: $idempotencyKey) { inventoryAdjustmentGroup { reason referenceDocumentUri changes { name delta quantityAfterChange } } userErrors { code field message } } }",
   "variables": {
      "input": {
        "name": "available",
        "reason": "correction",
        "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
        "quantities": [
          {
            "inventoryItemId": "gid://shopify/InventoryItem/30322695",
            "locationId": "gid://shopify/Location/124656943",
            "quantity": 42,
            "changeFromQuantity": 1
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
    mutation inventorySetQuantities($input: InventorySetQuantitiesInput!, $idempotencyKey: String!) {
      inventorySetQuantities(input: $input) @idempotent(key: $idempotencyKey) {
        inventoryAdjustmentGroup {
          reason
          referenceDocumentUri
          changes {
            name
            delta
            quantityAfterChange
          }
        }
        userErrors {
          code
          field
          message
        }
      }
    }`,
    {
      variables: {
          "input": {
              "name": "available",
              "reason": "correction",
              "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
              "quantities": [
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 42,
                      "changeFromQuantity": 1
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
    mutation inventorySetQuantities($input: InventorySetQuantitiesInput!, $idempotencyKey: String!) {
      inventorySetQuantities(input: $input) @idempotent(key: $idempotencyKey) {
        inventoryAdjustmentGroup {
          reason
          referenceDocumentUri
          changes {
            name
            delta
            quantityAfterChange
          }
        }
        userErrors {
          code
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "name": "available",
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "quantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 42,
          "changeFromQuantity": 1
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
      "query": `mutation inventorySetQuantities($input: InventorySetQuantitiesInput!, $idempotencyKey: String!) {
        inventorySetQuantities(input: $input) @idempotent(key: $idempotencyKey) {
          inventoryAdjustmentGroup {
            reason
            referenceDocumentUri
            changes {
              name
              delta
              quantityAfterChange
            }
          }
          userErrors {
            code
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "name": "available",
              "reason": "correction",
              "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
              "quantities": [
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 42,
                      "changeFromQuantity": 1
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
  'mutation inventorySetQuantities($input: InventorySetQuantitiesInput!, $idempotencyKey: String!) {
    inventorySetQuantities(input: $input) @idempotent(key: $idempotencyKey) {
      inventoryAdjustmentGroup {
        reason
        referenceDocumentUri
        changes {
          name
          delta
          quantityAfterChange
        }
      }
      userErrors {
        code
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "name": "available",
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "quantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 42,
          "changeFromQuantity": 1
        }
      ]
    },
    "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000"
  }'
  ```

  #### Response

  ```json
  {
    "inventorySetQuantities": {
      "inventoryAdjustmentGroup": {
        "reason": "Inventory correction",
        "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
        "changes": [
          {
            "name": "available",
            "delta": 41,
            "quantityAfterChange": null
          },
          {
            "name": "on_hand",
            "delta": 41,
            "quantityAfterChange": null
          }
        ]
      },
      "userErrors": []
    }
  }
  ```

* ### Setting available quantity at a location with compare-and-swap (CAS) enabled

  #### Query

  ```graphql
  mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
    inventorySetQuantities(input: $input) {
      inventoryAdjustmentGroup {
        reason
        referenceDocumentUri
        changes {
          name
          delta
          quantityAfterChange
        }
      }
      userErrors {
        code
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "name": "available",
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "quantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 11,
          "compareQuantity": 1
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
  "query": "mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) { inventorySetQuantities(input: $input) { inventoryAdjustmentGroup { reason referenceDocumentUri changes { name delta quantityAfterChange } } userErrors { code field message } } }",
   "variables": {
      "input": {
        "name": "available",
        "reason": "correction",
        "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
        "quantities": [
          {
            "inventoryItemId": "gid://shopify/InventoryItem/30322695",
            "locationId": "gid://shopify/Location/124656943",
            "quantity": 11,
            "compareQuantity": 1
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
    mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
      inventorySetQuantities(input: $input) {
        inventoryAdjustmentGroup {
          reason
          referenceDocumentUri
          changes {
            name
            delta
            quantityAfterChange
          }
        }
        userErrors {
          code
          field
          message
        }
      }
    }`,
    {
      variables: {
          "input": {
              "name": "available",
              "reason": "correction",
              "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
              "quantities": [
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 11,
                      "compareQuantity": 1
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
    mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
      inventorySetQuantities(input: $input) {
        inventoryAdjustmentGroup {
          reason
          referenceDocumentUri
          changes {
            name
            delta
            quantityAfterChange
          }
        }
        userErrors {
          code
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "name": "available",
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "quantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 11,
          "compareQuantity": 1
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
      "query": `mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
        inventorySetQuantities(input: $input) {
          inventoryAdjustmentGroup {
            reason
            referenceDocumentUri
            changes {
              name
              delta
              quantityAfterChange
            }
          }
          userErrors {
            code
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "name": "available",
              "reason": "correction",
              "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
              "quantities": [
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 11,
                      "compareQuantity": 1
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
  'mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
    inventorySetQuantities(input: $input) {
      inventoryAdjustmentGroup {
        reason
        referenceDocumentUri
        changes {
          name
          delta
          quantityAfterChange
        }
      }
      userErrors {
        code
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "name": "available",
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "quantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 11,
          "compareQuantity": 1
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "inventorySetQuantities": {
      "inventoryAdjustmentGroup": {
        "reason": "Inventory correction",
        "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
        "changes": [
          {
            "name": "available",
            "delta": 10,
            "quantityAfterChange": null
          },
          {
            "name": "on_hand",
            "delta": 10,
            "quantityAfterChange": null
          }
        ]
      },
      "userErrors": []
    }
  }
  ```

* ### Setting available quantity at a location without compare-and-swap (CAS) enabled

  #### Query

  ```graphql
  mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
    inventorySetQuantities(input: $input) {
      inventoryAdjustmentGroup {
        reason
        referenceDocumentUri
        changes {
          name
          delta
          quantityAfterChange
        }
      }
      userErrors {
        code
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "ignoreCompareQuantity": true,
      "name": "available",
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "quantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 42,
          "compareQuantity": null
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
  "query": "mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) { inventorySetQuantities(input: $input) { inventoryAdjustmentGroup { reason referenceDocumentUri changes { name delta quantityAfterChange } } userErrors { code field message } } }",
   "variables": {
      "input": {
        "ignoreCompareQuantity": true,
        "name": "available",
        "reason": "correction",
        "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
        "quantities": [
          {
            "inventoryItemId": "gid://shopify/InventoryItem/30322695",
            "locationId": "gid://shopify/Location/124656943",
            "quantity": 42,
            "compareQuantity": null
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
    mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
      inventorySetQuantities(input: $input) {
        inventoryAdjustmentGroup {
          reason
          referenceDocumentUri
          changes {
            name
            delta
            quantityAfterChange
          }
        }
        userErrors {
          code
          field
          message
        }
      }
    }`,
    {
      variables: {
          "input": {
              "ignoreCompareQuantity": true,
              "name": "available",
              "reason": "correction",
              "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
              "quantities": [
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 42,
                      "compareQuantity": null
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
    mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
      inventorySetQuantities(input: $input) {
        inventoryAdjustmentGroup {
          reason
          referenceDocumentUri
          changes {
            name
            delta
            quantityAfterChange
          }
        }
        userErrors {
          code
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "ignoreCompareQuantity": true,
      "name": "available",
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "quantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 42,
          "compareQuantity": null
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
      "query": `mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
        inventorySetQuantities(input: $input) {
          inventoryAdjustmentGroup {
            reason
            referenceDocumentUri
            changes {
              name
              delta
              quantityAfterChange
            }
          }
          userErrors {
            code
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "ignoreCompareQuantity": true,
              "name": "available",
              "reason": "correction",
              "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
              "quantities": [
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "locationId": "gid://shopify/Location/124656943",
                      "quantity": 42,
                      "compareQuantity": null
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
  'mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
    inventorySetQuantities(input: $input) {
      inventoryAdjustmentGroup {
        reason
        referenceDocumentUri
        changes {
          name
          delta
          quantityAfterChange
        }
      }
      userErrors {
        code
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "ignoreCompareQuantity": true,
      "name": "available",
      "reason": "correction",
      "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
      "quantities": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "quantity": 42,
          "compareQuantity": null
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "inventorySetQuantities": {
      "inventoryAdjustmentGroup": {
        "reason": "Inventory correction",
        "referenceDocumentUri": "logistics://some.warehouse/take/2023-01-23T13:14:15Z",
        "changes": [
          {
            "name": "available",
            "delta": 41,
            "quantityAfterChange": null
          },
          {
            "name": "on_hand",
            "delta": 41,
            "quantityAfterChange": null
          }
        ]
      },
      "userErrors": []
    }
  }
  ```

* ### inventorySetQuantities reference
