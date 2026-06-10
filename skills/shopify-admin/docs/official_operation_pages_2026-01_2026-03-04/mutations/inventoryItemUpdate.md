---
title: inventoryItemUpdate - GraphQL Admin
description: >-
  Updates an
  [`InventoryItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryItem)'s
  properties including whether inventory is tracked, cost, SKU, and whether
  shipping is required. Inventory items represent the goods available to be
  shipped to customers.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventoryItemUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventoryItemUpdate.md
---

# inventory​Item​Update

mutation

Requires `write_inventory` access scope. Also: The user must have a permission to update an inventory item.

Updates an [`InventoryItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryItem)'s properties including whether inventory is tracked, cost, SKU, and whether shipping is required. Inventory items represent the goods available to be shipped to customers.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the inventory item to update.

* input

  [Inventory​Item​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/InventoryItemInput)

  required

  The input fields that update an [`inventoryItem`](https://shopify.dev/api/admin-graphql/latest/queries/inventoryitem).

***

## Inventory​Item​Update​Payload returns

* inventory​Item

  [Inventory​Item](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryItem)

  The inventory item that was updated.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Updates an existing inventory item

  #### Query

  ```graphql
  mutation inventoryItemUpdate($id: ID!, $input: InventoryItemInput!) {
    inventoryItemUpdate(id: $id, input: $input) {
      inventoryItem {
        id
        unitCost {
          amount
        }
        tracked
        countryCodeOfOrigin
        provinceCodeOfOrigin
        harmonizedSystemCode
        countryHarmonizedSystemCodes(first: 1) {
          edges {
            node {
              harmonizedSystemCode
              countryCode
            }
          }
        }
      }
      userErrors {
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/InventoryItem/43729076",
    "input": {
      "cost": 145.89,
      "tracked": false,
      "countryCodeOfOrigin": "US",
      "provinceCodeOfOrigin": "OR",
      "harmonizedSystemCode": "621710",
      "countryHarmonizedSystemCodes": [
        {
          "harmonizedSystemCode": "6217109510",
          "countryCode": "CA"
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
  "query": "mutation inventoryItemUpdate($id: ID!, $input: InventoryItemInput!) { inventoryItemUpdate(id: $id, input: $input) { inventoryItem { id unitCost { amount } tracked countryCodeOfOrigin provinceCodeOfOrigin harmonizedSystemCode countryHarmonizedSystemCodes(first: 1) { edges { node { harmonizedSystemCode countryCode } } } } userErrors { message } } }",
   "variables": {
      "id": "gid://shopify/InventoryItem/43729076",
      "input": {
        "cost": 145.89,
        "tracked": false,
        "countryCodeOfOrigin": "US",
        "provinceCodeOfOrigin": "OR",
        "harmonizedSystemCode": "621710",
        "countryHarmonizedSystemCodes": [
          {
            "harmonizedSystemCode": "6217109510",
            "countryCode": "CA"
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
    mutation inventoryItemUpdate($id: ID!, $input: InventoryItemInput!) {
      inventoryItemUpdate(id: $id, input: $input) {
        inventoryItem {
          id
          unitCost {
            amount
          }
          tracked
          countryCodeOfOrigin
          provinceCodeOfOrigin
          harmonizedSystemCode
          countryHarmonizedSystemCodes(first: 1) {
            edges {
              node {
                harmonizedSystemCode
                countryCode
              }
            }
          }
        }
        userErrors {
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/InventoryItem/43729076",
          "input": {
              "cost": 145.89,
              "tracked": false,
              "countryCodeOfOrigin": "US",
              "provinceCodeOfOrigin": "OR",
              "harmonizedSystemCode": "621710",
              "countryHarmonizedSystemCodes": [
                  {
                      "harmonizedSystemCode": "6217109510",
                      "countryCode": "CA"
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
    mutation inventoryItemUpdate($id: ID!, $input: InventoryItemInput!) {
      inventoryItemUpdate(id: $id, input: $input) {
        inventoryItem {
          id
          unitCost {
            amount
          }
          tracked
          countryCodeOfOrigin
          provinceCodeOfOrigin
          harmonizedSystemCode
          countryHarmonizedSystemCodes(first: 1) {
            edges {
              node {
                harmonizedSystemCode
                countryCode
              }
            }
          }
        }
        userErrors {
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/InventoryItem/43729076",
    "input": {
      "cost": 145.89,
      "tracked": false,
      "countryCodeOfOrigin": "US",
      "provinceCodeOfOrigin": "OR",
      "harmonizedSystemCode": "621710",
      "countryHarmonizedSystemCodes": [
        {
          "harmonizedSystemCode": "6217109510",
          "countryCode": "CA"
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
      "query": `mutation inventoryItemUpdate($id: ID!, $input: InventoryItemInput!) {
        inventoryItemUpdate(id: $id, input: $input) {
          inventoryItem {
            id
            unitCost {
              amount
            }
            tracked
            countryCodeOfOrigin
            provinceCodeOfOrigin
            harmonizedSystemCode
            countryHarmonizedSystemCodes(first: 1) {
              edges {
                node {
                  harmonizedSystemCode
                  countryCode
                }
              }
            }
          }
          userErrors {
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/InventoryItem/43729076",
          "input": {
              "cost": 145.89,
              "tracked": false,
              "countryCodeOfOrigin": "US",
              "provinceCodeOfOrigin": "OR",
              "harmonizedSystemCode": "621710",
              "countryHarmonizedSystemCodes": [
                  {
                      "harmonizedSystemCode": "6217109510",
                      "countryCode": "CA"
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
  'mutation inventoryItemUpdate($id: ID!, $input: InventoryItemInput!) {
    inventoryItemUpdate(id: $id, input: $input) {
      inventoryItem {
        id
        unitCost {
          amount
        }
        tracked
        countryCodeOfOrigin
        provinceCodeOfOrigin
        harmonizedSystemCode
        countryHarmonizedSystemCodes(first: 1) {
          edges {
            node {
              harmonizedSystemCode
              countryCode
            }
          }
        }
      }
      userErrors {
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/InventoryItem/43729076",
    "input": {
      "cost": 145.89,
      "tracked": false,
      "countryCodeOfOrigin": "US",
      "provinceCodeOfOrigin": "OR",
      "harmonizedSystemCode": "621710",
      "countryHarmonizedSystemCodes": [
        {
          "harmonizedSystemCode": "6217109510",
          "countryCode": "CA"
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "inventoryItemUpdate": {
      "inventoryItem": {
        "id": "gid://shopify/InventoryItem/43729076",
        "unitCost": {
          "amount": "145.89"
        },
        "tracked": false,
        "countryCodeOfOrigin": "US",
        "provinceCodeOfOrigin": "OR",
        "harmonizedSystemCode": "621710",
        "countryHarmonizedSystemCodes": {
          "edges": [
            {
              "node": {
                "harmonizedSystemCode": "6217109510",
                "countryCode": "CA"
              }
            }
          ]
        }
      },
      "userErrors": []
    }
  }
  ```

* ### inventoryItemUpdate reference
