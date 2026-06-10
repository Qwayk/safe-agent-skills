---
title: catalogs - GraphQL Admin
description: >-
  Returns a paginated list of catalogs for the shop. Catalogs control which
  products are published and how they're priced in different contexts, such as
  international markets (Canada vs. United States), B2B company locations
  (different branches of the same business), or specific sales channels (such as
  online store vs. POS).


  Filter catalogs by
  [`type`](https://shopify.dev/docs/api/admin-graphql/latest/queries/catalogs#arguments-type)
  and use the
  [`query`](https://shopify.dev/docs/api/admin-graphql/latest/queries/catalogs#arguments-query)
  argument to search and filter by additional criteria.


  Learn more about [Shopify
  Catalogs](https://shopify.dev/docs/apps/build/markets/catalogs-different-markets).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/catalogs'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/catalogs.md'
---

# catalogs

query

Returns a paginated list of catalogs for the shop. Catalogs control which products are published and how they're priced in different contexts, such as international markets (Canada vs. United States), B2B company locations (different branches of the same business), or specific sales channels (such as online store vs. POS).

Filter catalogs by [`type`](https://shopify.dev/docs/api/admin-graphql/latest/queries/catalogs#arguments-type) and use the [`query`](https://shopify.dev/docs/api/admin-graphql/latest/queries/catalogs#arguments-query) argument to search and filter by additional criteria.

Learn more about [Shopify Catalogs](https://shopify.dev/docs/apps/build/markets/catalogs-different-markets).

## CatalogConnection arguments

[CatalogConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/CatalogConnection)

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

  * * default

      string

    * app\_id

      id

    - Filter by a case-insensitive search of multiple fields in a document.

    - Example:
      * `query=Bob Norman`
      * `query=title:green hoodie`

  * company\_id

    id

  * company\_location\_id

    id

  * * id

      id

    * managed\_country\_id

      id

    - Filter by `id` range.

    - Example:
      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

  * market\_id

    id

  * status

    string

  * title

    string

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* sort​Key

  [Catalog​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/CatalogSortKeys)

  Default:ID

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

* type

  [Catalog​Type](https://shopify.dev/docs/api/admin-graphql/latest/enums/CatalogType)

  Default:null

  The type of the catalogs to be returned.

***

## Possible returns

* edges

  [\[Catalog​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CatalogEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Catalog!\]!](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Catalog)

  non-null

  A list of nodes that are contained in CatalogEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Filter catalogs by type

  #### Query

  ```graphql
  query {
    catalogs(first: 3, type: MARKET) {
      nodes {
        id
        title
        status
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
  "query": "query { catalogs(first: 3, type: MARKET) { nodes { id title status } } }"
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
      catalogs(first: 3, type: MARKET) {
        nodes {
          id
          title
          status
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
      catalogs(first: 3, type: MARKET) {
        nodes {
          id
          title
          status
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
      catalogs(first: 3, type: MARKET) {
        nodes {
          id
          title
          status
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
    catalogs(first: 3, type: MARKET) {
      nodes {
        id
        title
        status
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "catalogs": {
      "nodes": [
        {
          "id": "gid://shopify/MarketCatalog/1068177673",
          "title": "NA Market",
          "status": "ACTIVE"
        },
        {
          "id": "gid://shopify/MarketCatalog/1068177676",
          "title": "Asia Market",
          "status": "DRAFT"
        },
        {
          "id": "gid://shopify/MarketCatalog/1068177677",
          "title": "Scandinavia Market",
          "status": "ARCHIVED"
        }
      ]
    }
  }
  ```

* ### List the first three catalogs in the shop

  #### Query

  ```graphql
  query {
    catalogs(first: 3) {
      nodes {
        id
        title
        status
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
  "query": "query { catalogs(first: 3) { nodes { id title status } } }"
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
      catalogs(first: 3) {
        nodes {
          id
          title
          status
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
      catalogs(first: 3) {
        nodes {
          id
          title
          status
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
      catalogs(first: 3) {
        nodes {
          id
          title
          status
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
    catalogs(first: 3) {
      nodes {
        id
        title
        status
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "catalogs": {
      "nodes": [
        {
          "id": "gid://shopify/MarketCatalog/1068177679",
          "title": "NA Market",
          "status": "ACTIVE"
        },
        {
          "id": "gid://shopify/CompanyLocationCatalog/1068177680",
          "title": "B2B Example 1",
          "status": "DRAFT"
        },
        {
          "id": "gid://shopify/AppCatalog/1068177681",
          "title": "App Catalog Example",
          "status": "ARCHIVED"
        }
      ]
    }
  }
  ```
