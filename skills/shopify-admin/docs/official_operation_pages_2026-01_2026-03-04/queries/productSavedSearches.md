---
title: productSavedSearches - GraphQL Admin
description: Returns a list of the shop's product saved searches.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/productSavedSearches
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/productSavedSearches.md
---

# product​Saved​Searches

query

Requires `read_products` access scope.

Returns a list of the shop's product saved searches.

## SavedSearchConnection arguments

[SavedSearchConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/SavedSearchConnection)

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

***

## Possible returns

* edges

  [\[Saved​Search​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SavedSearchEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Saved​Search!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SavedSearch)

  non-null

  A list of nodes that are contained in SavedSearchEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Retrieve the first three saved product searches

  #### Description

  Retrieve the first three saved product searches. A saved search is a specific search query that you can use to quickly find products. This example returns the first three saved product searches.

  #### Query

  ```graphql
  query {
    productSavedSearches(first: 3) {
      nodes {
        id
        legacyResourceId
        name
        filters {
          key
          value
        }
        query
        searchTerms
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
  "query": "query { productSavedSearches(first: 3) { nodes { id legacyResourceId name filters { key value } query searchTerms } } }"
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
      productSavedSearches(first: 3) {
        nodes {
          id
          legacyResourceId
          name
          filters {
            key
            value
          }
          query
          searchTerms
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
      productSavedSearches(first: 3) {
        nodes {
          id
          legacyResourceId
          name
          filters {
            key
            value
          }
          query
          searchTerms
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
      productSavedSearches(first: 3) {
        nodes {
          id
          legacyResourceId
          name
          filters {
            key
            value
          }
          query
          searchTerms
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
    productSavedSearches(first: 3) {
      nodes {
        id
        legacyResourceId
        name
        filters {
          key
          value
        }
        query
        searchTerms
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "productSavedSearches": {
      "nodes": [
        {
          "id": "gid://shopify/SavedSearch/136409974",
          "legacyResourceId": "136409974",
          "name": "Foo Products",
          "filters": [],
          "query": "foo",
          "searchTerms": "foo"
        },
        {
          "id": "gid://shopify/SavedSearch/1068136123",
          "legacyResourceId": "1068136123",
          "name": "Drafts",
          "filters": [
            {
              "key": "status",
              "value": "DRAFT"
            }
          ],
          "query": "status:\"DRAFT\"",
          "searchTerms": ""
        },
        {
          "id": "gid://shopify/SavedSearch/1068136124",
          "legacyResourceId": "1068136124",
          "name": "Products from Vendor X",
          "filters": [
            {
              "key": "vendor",
              "value": "Vendor X"
            }
          ],
          "query": "vendor:\"Vendor X\"",
          "searchTerms": ""
        }
      ]
    }
  }
  ```
