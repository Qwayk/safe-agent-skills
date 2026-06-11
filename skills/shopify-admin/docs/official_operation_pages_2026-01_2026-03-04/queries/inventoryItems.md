---
title: inventoryItems - GraphQL Admin
description: Returns a list of inventory items.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/inventoryItems'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/inventoryItems.md'
---

# inventory​Items

query

Returns a list of inventory items.

## InventoryItemConnection arguments

[InventoryItemConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/InventoryItemConnection)

* after

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* before

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* first

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* last

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* query

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

  * created\_at

    time

  * * id

      id

    * sku

      string

    * updated\_at

      time

    - Filter by `id` range.

    - Example:

      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

      Filter by the inventory item [`sku`](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryItem#field-sku) field. [Learn more about SKUs](https://help.shopify.com/manual/products/details/sku).

    - Example:
      * `sku:XYZ-12345`

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

***

## Possible returns

* edges

  [\[Inventory​Item​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryItemEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Inventory​Item!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryItem)

  non-null

  A list of nodes that are contained in InventoryItemEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Get details about the first 2 inventory items

  #### Query

  ```graphql
  query inventoryItems {
    inventoryItems(first: 2) {
      edges {
        node {
          id
          tracked
          sku
        }
      }
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
  "query": "query inventoryItems { inventoryItems(first: 2) { edges { node { id tracked sku } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query inventoryItems {
      inventoryItems(first: 2) {
        edges {
          node {
            id
            tracked
            sku
          }
        }
      }
    }`,
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
    query inventoryItems {
      inventoryItems(first: 2) {
        edges {
          node {
            id
            tracked
            sku
          }
        }
      }
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `query inventoryItems {
      inventoryItems(first: 2) {
        edges {
          node {
            id
            tracked
            sku
          }
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query inventoryItems {
    inventoryItems(first: 2) {
      edges {
        node {
          id
          tracked
          sku
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "inventoryItems": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/InventoryItem/30322695",
            "tracked": true,
            "sku": "element-151"
          }
        },
        {
          "node": {
            "id": "gid://shopify/InventoryItem/43729076",
            "tracked": true,
            "sku": "draft-151"
          }
        }
      ]
    }
  }
  ```

* ### Get details about the first inventory item matching an SKU

  #### Query

  ```graphql
  query inventoryItems {
    inventoryItems(first: 1, query: "sku:'element-151'") {
      edges {
        node {
          id
          tracked
          sku
        }
      }
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
  "query": "query inventoryItems { inventoryItems(first: 1, query: \"sku:'\''element-151'\''\") { edges { node { id tracked sku } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query inventoryItems {
      inventoryItems(first: 1, query: "sku:'element-151'") {
        edges {
          node {
            id
            tracked
            sku
          }
        }
      }
    }`,
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
    query inventoryItems {
      inventoryItems(first: 1, query: "sku:'element-151'") {
        edges {
          node {
            id
            tracked
            sku
          }
        }
      }
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `query inventoryItems {
      inventoryItems(first: 1, query: "sku:'element-151'") {
        edges {
          node {
            id
            tracked
            sku
          }
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query inventoryItems {
    inventoryItems(first: 1, query: "sku:'element-151'") {
      edges {
        node {
          id
          tracked
          sku
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "inventoryItems": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/InventoryItem/30322695",
            "tracked": true,
            "sku": "element-151"
          }
        }
      ]
    }
  }
  ```

* ### Get details about the first two inventory item with created\_at or matching sku

  #### Query

  ```graphql
  query inventoryItems {
    inventoryItems(first: 2, query: "(created_at:>2023-10-10) OR (sku:'element-151')") {
      edges {
        node {
          id
          tracked
          sku
        }
      }
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
  "query": "query inventoryItems { inventoryItems(first: 2, query: \"(created_at:>2023-10-10) OR (sku:'\''element-151'\'')\") { edges { node { id tracked sku } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query inventoryItems {
      inventoryItems(first: 2, query: "(created_at:>2023-10-10) OR (sku:'element-151')") {
        edges {
          node {
            id
            tracked
            sku
          }
        }
      }
    }`,
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
    query inventoryItems {
      inventoryItems(first: 2, query: "(created_at:>2023-10-10) OR (sku:'element-151')") {
        edges {
          node {
            id
            tracked
            sku
          }
        }
      }
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `query inventoryItems {
      inventoryItems(first: 2, query: "(created_at:>2023-10-10) OR (sku:'element-151')") {
        edges {
          node {
            id
            tracked
            sku
          }
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query inventoryItems {
    inventoryItems(first: 2, query: "(created_at:>2023-10-10) OR (sku:'element-151')") {
      edges {
        node {
          id
          tracked
          sku
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "inventoryItems": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/InventoryItem/30322695",
            "tracked": true,
            "sku": "element-151"
          }
        },
        {
          "node": {
            "id": "gid://shopify/InventoryItem/43729076",
            "tracked": true,
            "sku": "draft-151"
          }
        }
      ]
    }
  }
  ```

* ### Retrieves a detailed list for inventory items by IDs

  #### Query

  ```graphql
  query InventoryItemList {
    inventoryItems(first: 20, query: "id:>=30322695") {
      nodes {
        id
        createdAt
        countryCodeOfOrigin
        harmonizedSystemCode
        provinceCodeOfOrigin
        requiresShipping
        sku
        tracked
        unitCost {
          currencyCode
          amount
        }
        updatedAt
        countryHarmonizedSystemCodes(first: 250) {
          nodes {
            harmonizedSystemCode
            countryCode
          }
        }
      }
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
  "query": "query InventoryItemList { inventoryItems(first: 20, query: \"id:>=30322695\") { nodes { id createdAt countryCodeOfOrigin harmonizedSystemCode provinceCodeOfOrigin requiresShipping sku tracked unitCost { currencyCode amount } updatedAt countryHarmonizedSystemCodes(first: 250) { nodes { harmonizedSystemCode countryCode } } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query InventoryItemList {
      inventoryItems(first: 20, query: "id:>=30322695") {
        nodes {
          id
          createdAt
          countryCodeOfOrigin
          harmonizedSystemCode
          provinceCodeOfOrigin
          requiresShipping
          sku
          tracked
          unitCost {
            currencyCode
            amount
          }
          updatedAt
          countryHarmonizedSystemCodes(first: 250) {
            nodes {
              harmonizedSystemCode
              countryCode
            }
          }
        }
      }
    }`,
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
    query InventoryItemList {
      inventoryItems(first: 20, query: "id:>=30322695") {
        nodes {
          id
          createdAt
          countryCodeOfOrigin
          harmonizedSystemCode
          provinceCodeOfOrigin
          requiresShipping
          sku
          tracked
          unitCost {
            currencyCode
            amount
          }
          updatedAt
          countryHarmonizedSystemCodes(first: 250) {
            nodes {
              harmonizedSystemCode
              countryCode
            }
          }
        }
      }
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `query InventoryItemList {
      inventoryItems(first: 20, query: "id:>=30322695") {
        nodes {
          id
          createdAt
          countryCodeOfOrigin
          harmonizedSystemCode
          provinceCodeOfOrigin
          requiresShipping
          sku
          tracked
          unitCost {
            currencyCode
            amount
          }
          updatedAt
          countryHarmonizedSystemCodes(first: 250) {
            nodes {
              harmonizedSystemCode
              countryCode
            }
          }
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query InventoryItemList {
    inventoryItems(first: 20, query: "id:>=30322695") {
      nodes {
        id
        createdAt
        countryCodeOfOrigin
        harmonizedSystemCode
        provinceCodeOfOrigin
        requiresShipping
        sku
        tracked
        unitCost {
          currencyCode
          amount
        }
        updatedAt
        countryHarmonizedSystemCodes(first: 250) {
          nodes {
            harmonizedSystemCode
            countryCode
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "inventoryItems": {
      "nodes": [
        {
          "id": "gid://shopify/InventoryItem/30322695",
          "createdAt": "2024-11-07T16:22:10Z",
          "countryCodeOfOrigin": "DE",
          "harmonizedSystemCode": "123456",
          "provinceCodeOfOrigin": "QC",
          "requiresShipping": true,
          "sku": "element-151",
          "tracked": true,
          "unitCost": {
            "currencyCode": "USD",
            "amount": "1.23"
          },
          "updatedAt": "2024-11-07T16:22:10Z",
          "countryHarmonizedSystemCodes": {
            "nodes": [
              {
                "harmonizedSystemCode": "123456999333",
                "countryCode": "CA"
              }
            ]
          }
        },
        {
          "id": "gid://shopify/InventoryItem/43729076",
          "createdAt": "2024-11-07T16:22:10Z",
          "countryCodeOfOrigin": null,
          "harmonizedSystemCode": null,
          "provinceCodeOfOrigin": null,
          "requiresShipping": true,
          "sku": "draft-151",
          "tracked": true,
          "unitCost": null,
          "updatedAt": "2024-11-07T16:22:10Z",
          "countryHarmonizedSystemCodes": {
            "nodes": []
          }
        },
        {
          "id": "gid://shopify/InventoryItem/113711323",
          "createdAt": "2024-11-07T16:22:10Z",
          "countryCodeOfOrigin": "CA",
          "harmonizedSystemCode": "555555",
          "provinceCodeOfOrigin": "",
          "requiresShipping": true,
          "sku": "element-155",
          "tracked": true,
          "unitCost": {
            "currencyCode": "USD",
            "amount": "15.0"
          },
          "updatedAt": "2024-11-07T16:22:10Z",
          "countryHarmonizedSystemCodes": {
            "nodes": []
          }
        },
        {
          "id": "gid://shopify/InventoryItem/138327650",
          "createdAt": "2024-11-07T16:22:10Z",
          "countryCodeOfOrigin": null,
          "harmonizedSystemCode": null,
          "provinceCodeOfOrigin": null,
          "requiresShipping": true,
          "sku": "boots-10",
          "tracked": true,
          "unitCost": null,
          "updatedAt": "2024-11-07T16:22:10Z",
          "countryHarmonizedSystemCodes": {
            "nodes": []
          }
        },
        {
          "id": "gid://shopify/InventoryItem/236948360",
          "createdAt": "2024-11-07T16:22:10Z",
          "countryCodeOfOrigin": "FR",
          "harmonizedSystemCode": "654321",
          "provinceCodeOfOrigin": "",
          "requiresShipping": true,
          "sku": "element-158",
          "tracked": true,
          "unitCost": {
            "currencyCode": "USD",
            "amount": "20.0"
          },
          "updatedAt": "2024-11-07T16:22:10Z",
          "countryHarmonizedSystemCodes": {
            "nodes": []
          }
        },
        {
          "id": "gid://shopify/InventoryItem/330284860",
          "createdAt": "2024-11-07T16:22:10Z",
          "countryCodeOfOrigin": null,
          "harmonizedSystemCode": null,
          "provinceCodeOfOrigin": null,
          "requiresShipping": true,
          "sku": "unpublished_boots-12",
          "tracked": true,
          "unitCost": null,
          "updatedAt": "2024-11-07T16:22:10Z",
          "countryHarmonizedSystemCodes": {
            "nodes": []
          }
        },
        {
          "id": "gid://shopify/InventoryItem/389013007",
          "createdAt": "2024-11-07T16:22:10Z",
          "countryCodeOfOrigin": "CA",
          "harmonizedSystemCode": "123456",
          "provinceCodeOfOrigin": "ON",
          "requiresShipping": true,
          "sku": "crappy_shoes_red",
          "tracked": true,
          "unitCost": {
            "currencyCode": "USD",
            "amount": "20.0"
          },
          "updatedAt": "2024-11-07T16:22:10Z",
          "countryHarmonizedSystemCodes": {
            "nodes": []
          }
        },
        {
          "id": "gid://shopify/InventoryItem/419425742",
          "createdAt": "2024-11-07T16:22:10Z",
          "countryCodeOfOrigin": "DE",
          "harmonizedSystemCode": "999999",
          "provinceCodeOfOrigin": null,
          "requiresShipping": true,
          "sku": "crappy_shoes_pink",
          "tracked": true,
          "unitCost": {
            "currencyCode": "USD",
            "amount": "20.0"
          },
          "updatedAt": "2024-11-07T16:22:10Z",
          "countryHarmonizedSystemCodes": {
            "nodes": []
          }
        },
        {
          "id": "gid://shopify/InventoryItem/438458761",
          "createdAt": "2024-11-07T16:22:10Z",
          "countryCodeOfOrigin": null,
          "harmonizedSystemCode": null,
          "provinceCodeOfOrigin": null,
          "requiresShipping": true,
          "sku": "IPOD2008RED",
          "tracked": true,
          "unitCost": null,
          "updatedAt": "2024-11-07T16:22:10Z",
          "countryHarmonizedSystemCodes": {
            "nodes": []
          }
        },
        {
          "id": "gid://shopify/InventoryItem/445365074",
          "createdAt": "2024-11-07T16:22:10Z",
          "countryCodeOfOrigin": "IT",
          "harmonizedSystemCode": "654321",
          "provinceCodeOfOrigin": "",
          "requiresShipping": true,
          "sku": "crappy_shoes_green",
          "tracked": true,
          "unitCost": {
            "currencyCode": "USD",
            "amount": "20.0"
          },
          "updatedAt": "2024-11-07T16:22:10Z",
          "countryHarmonizedSystemCodes": {
            "nodes": []
          }
        },
        {
          "id": "gid://shopify/InventoryItem/498744621",
          "createdAt": "2024-11-07T16:22:10Z",
          "countryCodeOfOrigin": null,
          "harmonizedSystemCode": null,
          "provinceCodeOfOrigin": null,
          "requiresShipping": true,
          "sku": "seo-boots-10",
          "tracked": true,
          "unitCost": {
            "currencyCode": "USD",
            "amount": "15.0"
          },
          "updatedAt": "2024-11-07T16:22:10Z",
          "countryHarmonizedSystemCodes": {
            "nodes": []
          }
        },
        {
          "id": "gid://shopify/InventoryItem/715806386",
          "createdAt": "2024-11-07T16:22:10Z",
          "countryCodeOfOrigin": "FR",
          "harmonizedSystemCode": "555555",
          "provinceCodeOfOrigin": "",
          "requiresShipping": true,
          "sku": "crappy_shoes_blue",
          "tracked": true,
          "unitCost": {
            "currencyCode": "USD",
            "amount": "20.0"
          },
          "updatedAt": "2024-11-07T16:22:10Z",
          "countryHarmonizedSystemCodes": {
            "nodes": []
          }
        }
      ]
    }
  }
  ```
