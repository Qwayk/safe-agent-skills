---
title: priceLists - GraphQL Admin
description: All price lists for a shop.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/priceLists'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/priceLists.md'
---

# price​Lists

query

All price lists for a shop.

## PriceListConnection arguments

[PriceListConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/PriceListConnection)

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

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* sort​Key

  [Price​List​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/PriceListSortKeys)

  Default:ID

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Price​List​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PriceListEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Price​List!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PriceList)

  non-null

  A list of nodes that are contained in PriceListEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Retrieve price list in reversed order

  #### Description

  Fetch the first price list and return the ID, currency, fixed prices count and catalog information

  #### Query

  ```graphql
  query {
    priceLists(first: 1, reverse: true) {
      nodes {
        id
        currency
        fixedPricesCount
        catalog {
          id
          title
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
  "query": "query { priceLists(first: 1, reverse: true) { nodes { id currency fixedPricesCount catalog { id title } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query {
      priceLists(first: 1, reverse: true) {
        nodes {
          id
          currency
          fixedPricesCount
          catalog {
            id
            title
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
    query {
      priceLists(first: 1, reverse: true) {
        nodes {
          id
          currency
          fixedPricesCount
          catalog {
            id
            title
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
    data: `query {
      priceLists(first: 1, reverse: true) {
        nodes {
          id
          currency
          fixedPricesCount
          catalog {
            id
            title
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
  'query {
    priceLists(first: 1, reverse: true) {
      nodes {
        id
        currency
        fixedPricesCount
        catalog {
          id
          title
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "priceLists": {
      "nodes": [
        {
          "id": "gid://shopify/PriceList/1014716632",
          "currency": "USD",
          "fixedPricesCount": 0,
          "catalog": null
        }
      ]
    }
  }
  ```

* ### Retrieve the ID, name, currency and quantity rules information

  #### Description

  Fetch the first price list and retrieves the ID, currency, and fetches the first three fixed quantity rules associated with that price list, including the increment, maximum, minimum values for each rule, and the product variant it is on.

  #### Query

  ```graphql
  query {
    priceLists(first: 1) {
      nodes {
        id
        name
        currency
        quantityRules(first: 3, originType: FIXED) {
          nodes {
            increment
            maximum
            minimum
            productVariant {
              id
              title
            }
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
  "query": "query { priceLists(first: 1) { nodes { id name currency quantityRules(first: 3, originType: FIXED) { nodes { increment maximum minimum productVariant { id title } } } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query {
      priceLists(first: 1) {
        nodes {
          id
          name
          currency
          quantityRules(first: 3, originType: FIXED) {
            nodes {
              increment
              maximum
              minimum
              productVariant {
                id
                title
              }
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
    query {
      priceLists(first: 1) {
        nodes {
          id
          name
          currency
          quantityRules(first: 3, originType: FIXED) {
            nodes {
              increment
              maximum
              minimum
              productVariant {
                id
                title
              }
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
    data: `query {
      priceLists(first: 1) {
        nodes {
          id
          name
          currency
          quantityRules(first: 3, originType: FIXED) {
            nodes {
              increment
              maximum
              minimum
              productVariant {
                id
                title
              }
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
  'query {
    priceLists(first: 1) {
      nodes {
        id
        name
        currency
        quantityRules(first: 3, originType: FIXED) {
          nodes {
            increment
            maximum
            minimum
            productVariant {
              id
              title
            }
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "priceLists": {
      "nodes": [
        {
          "id": "gid://shopify/PriceList/225060712",
          "name": "price_list_with_quantity_rules",
          "currency": "USD",
          "quantityRules": {
            "nodes": [
              {
                "increment": 100,
                "maximum": 5000,
                "minimum": 500,
                "productVariant": {
                  "id": "gid://shopify/ProductVariant/43729076",
                  "title": "151cm"
                }
              },
              {
                "increment": 10,
                "maximum": 1000,
                "minimum": 100,
                "productVariant": {
                  "id": "gid://shopify/ProductVariant/138327650",
                  "title": "Default"
                }
              },
              {
                "increment": 5,
                "maximum": null,
                "minimum": 10,
                "productVariant": {
                  "id": "gid://shopify/ProductVariant/389013007",
                  "title": "Small"
                }
              }
            ]
          }
        }
      ]
    }
  }
  ```

* ### Retrieve the first two price lists

  #### Description

  Fetches the first two price lists. For each price list, it retrieves the ID, name, currency, and the count of fixed prices. It also fetches the adjustment type and value of the price list.

  #### Query

  ```graphql
  query {
    priceLists(first: 2) {
      edges {
        node {
          id
          name
          currency
          fixedPricesCount
          parent {
            adjustment {
              type
              value
            }
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
  "query": "query { priceLists(first: 2) { edges { node { id name currency fixedPricesCount parent { adjustment { type value } } } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query {
      priceLists(first: 2) {
        edges {
          node {
            id
            name
            currency
            fixedPricesCount
            parent {
              adjustment {
                type
                value
              }
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
    query {
      priceLists(first: 2) {
        edges {
          node {
            id
            name
            currency
            fixedPricesCount
            parent {
              adjustment {
                type
                value
              }
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
    data: `query {
      priceLists(first: 2) {
        edges {
          node {
            id
            name
            currency
            fixedPricesCount
            parent {
              adjustment {
                type
                value
              }
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
  'query {
    priceLists(first: 2) {
      edges {
        node {
          id
          name
          currency
          fixedPricesCount
          parent {
            adjustment {
              type
              value
            }
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "priceLists": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/PriceList/11668351",
            "name": "location_price_list",
            "currency": "USD",
            "fixedPricesCount": 0,
            "parent": {
              "adjustment": {
                "type": "PERCENTAGE_DECREASE",
                "value": 50
              }
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/PriceList/36142538",
            "name": "relative_pricelist_nullify",
            "currency": "CAD",
            "fixedPricesCount": 0,
            "parent": {
              "adjustment": {
                "type": "PERCENTAGE_DECREASE",
                "value": 5
              }
            }
          }
        }
      ]
    }
  }
  ```
