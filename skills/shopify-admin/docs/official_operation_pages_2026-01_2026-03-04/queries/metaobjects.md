---
title: metaobjects - GraphQL Admin
description: >-
  Returns a paginated list of
  [`Metaobject`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Metaobject)
  entries for a specific type. Metaobjects are custom data structures that
  extend Shopify's data model with merchant or app-specific data types.


  Filter results using the query parameter with a search syntax for metaobject
  fields. Use `fields.{key}:{value}` to filter by field values, supporting any
  field previously marked as filterable. The `sortKey` parameter accepts `id`,
  `type`, `updated_at`, or `display_name` to control result ordering.


  Learn more about [querying metaobjects by field
  value](https://shopify.dev/docs/apps/build/custom-data/metafields/query-by-metafield-value).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/metaobjects'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/metaobjects.md'
---

# metaobjects

query

Requires `read_metaobjects` access scope.

Returns a paginated list of [`Metaobject`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Metaobject) entries for a specific type. Metaobjects are custom data structures that extend Shopify's data model with merchant or app-specific data types.

Filter results using the query parameter with a search syntax for metaobject fields. Use `fields.{key}:{value}` to filter by field values, supporting any field previously marked as filterable. The `sortKey` parameter accepts `id`, `type`, `updated_at`, or `display_name` to control result ordering.

Learn more about [querying metaobjects by field value](https://shopify.dev/docs/apps/build/custom-data/metafields/query-by-metafield-value).

## MetaobjectConnection arguments

[MetaobjectConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/MetaobjectConnection)

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

  * display\_name

    string

  * * fields.{key}

      mixed

    * handle

      string

    - Filters metaobject entries by field value. Format: `fields.{key}:{value}`. Only fields marked as filterable in the metaobject definition can be used. Learn more about [querying metaobjects by field value](https://shopify.dev/apps/build/custom-data/metafields/query-by-metafield-value).

    - Example:
      * `fields.color:blue`
      * `fields.on_sale:true`

  * * id

      id

    * updated\_at

      time

    - Filter by `id` range.

    - Example:
      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* sort​Key

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The key of a field to sort with. Supports "id", "type", "updated\_at", and "display\_name".

* type

  [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  The type of the metaobjects to query.

***

## Possible returns

* edges

  [\[Metaobject​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Metaobject!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Metaobject)

  non-null

  A list of nodes that are contained in MetaobjectEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Fetch all metaobjects

  #### Description

  Fetch the full list of metaobjects entries of some provided type.

  #### Query

  ```graphql
  query Metaobjects {
    metaobjects(type: "$app:author", first: 10) {
      nodes {
        handle
        fullName: field(key: "full_name") {
          jsonValue
        }
        firstPublished: field(key: "first_published") {
          jsonValue
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
  "query": "query Metaobjects { metaobjects(type: \"$app:author\", first: 10) { nodes { handle fullName: field(key: \"full_name\") { jsonValue } firstPublished: field(key: \"first_published\") { jsonValue } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query Metaobjects {
      metaobjects(type: "$app:author", first: 10) {
        nodes {
          handle
          fullName: field(key: "full_name") {
            jsonValue
          }
          firstPublished: field(key: "first_published") {
            jsonValue
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
    query Metaobjects {
      metaobjects(type: "$app:author", first: 10) {
        nodes {
          handle
          fullName: field(key: "full_name") {
            jsonValue
          }
          firstPublished: field(key: "first_published") {
            jsonValue
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
    data: `query Metaobjects {
      metaobjects(type: "$app:author", first: 10) {
        nodes {
          handle
          fullName: field(key: "full_name") {
            jsonValue
          }
          firstPublished: field(key: "first_published") {
            jsonValue
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
  'query Metaobjects {
    metaobjects(type: "$app:author", first: 10) {
      nodes {
        handle
        fullName: field(key: "full_name") {
          jsonValue
        }
        firstPublished: field(key: "first_published") {
          jsonValue
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "metaobjects": {
      "nodes": [
        {
          "handle": "jane-austen",
          "fullName": {
            "jsonValue": "Jane Austen"
          },
          "firstPublished": {
            "jsonValue": 1811
          }
        }
      ]
    }
  }
  ```

* ### Fetch metaobjects with matching values

  #### Description

  Fetch the metaobjects entries with matching values for a given field.

  #### Query

  ```graphql
  query Metaobjects {
    metaobjects(first: 10, type: "$app:author", query: "fields.first_published:<=1900") {
      nodes {
        handle
        fullName: field(key: "full_name") {
          jsonValue
        }
        firstPublished: field(key: "first_published") {
          jsonValue
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
  "query": "query Metaobjects { metaobjects(first: 10, type: \"$app:author\", query: \"fields.first_published:<=1900\") { nodes { handle fullName: field(key: \"full_name\") { jsonValue } firstPublished: field(key: \"first_published\") { jsonValue } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query Metaobjects {
      metaobjects(first: 10, type: "$app:author", query: "fields.first_published:<=1900") {
        nodes {
          handle
          fullName: field(key: "full_name") {
            jsonValue
          }
          firstPublished: field(key: "first_published") {
            jsonValue
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
    query Metaobjects {
      metaobjects(first: 10, type: "$app:author", query: "fields.first_published:<=1900") {
        nodes {
          handle
          fullName: field(key: "full_name") {
            jsonValue
          }
          firstPublished: field(key: "first_published") {
            jsonValue
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
    data: `query Metaobjects {
      metaobjects(first: 10, type: "$app:author", query: "fields.first_published:<=1900") {
        nodes {
          handle
          fullName: field(key: "full_name") {
            jsonValue
          }
          firstPublished: field(key: "first_published") {
            jsonValue
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
  'query Metaobjects {
    metaobjects(first: 10, type: "$app:author", query: "fields.first_published:<=1900") {
      nodes {
        handle
        fullName: field(key: "full_name") {
          jsonValue
        }
        firstPublished: field(key: "first_published") {
          jsonValue
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "metaobjects": {
      "nodes": [
        {
          "handle": "jane-austen",
          "fullName": {
            "jsonValue": "Jane Austen"
          },
          "firstPublished": {
            "jsonValue": 1811
          }
        }
      ]
    }
  }
  ```

* ### Fetch metaobjects with pagination

  #### Description

  Fetch a page of metaobjects entries of some provided type.

  #### Query

  ```graphql
  query Metaobjects($cursor: String) {
    metaobjects(type: "$app:author", first: 10, after: $cursor) {
      pageInfo {
        hasNextPage
        endCursor
      }
      edges {
        node {
          handle
          fullName: field(key: "full_name") {
            jsonValue
          }
          firstPublished: field(key: "first_published") {
            jsonValue
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
  "query": "query Metaobjects($cursor: String) { metaobjects(type: \"$app:author\", first: 10, after: $cursor) { pageInfo { hasNextPage endCursor } edges { node { handle fullName: field(key: \"full_name\") { jsonValue } firstPublished: field(key: \"first_published\") { jsonValue } } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query Metaobjects($cursor: String) {
      metaobjects(type: "$app:author", first: 10, after: $cursor) {
        pageInfo {
          hasNextPage
          endCursor
        }
        edges {
          node {
            handle
            fullName: field(key: "full_name") {
              jsonValue
            }
            firstPublished: field(key: "first_published") {
              jsonValue
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
    query Metaobjects($cursor: String) {
      metaobjects(type: "$app:author", first: 10, after: $cursor) {
        pageInfo {
          hasNextPage
          endCursor
        }
        edges {
          node {
            handle
            fullName: field(key: "full_name") {
              jsonValue
            }
            firstPublished: field(key: "first_published") {
              jsonValue
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
    data: `query Metaobjects($cursor: String) {
      metaobjects(type: "$app:author", first: 10, after: $cursor) {
        pageInfo {
          hasNextPage
          endCursor
        }
        edges {
          node {
            handle
            fullName: field(key: "full_name") {
              jsonValue
            }
            firstPublished: field(key: "first_published") {
              jsonValue
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
  'query Metaobjects($cursor: String) {
    metaobjects(type: "$app:author", first: 10, after: $cursor) {
      pageInfo {
        hasNextPage
        endCursor
      }
      edges {
        node {
          handle
          fullName: field(key: "full_name") {
            jsonValue
          }
          firstPublished: field(key: "first_published") {
            jsonValue
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "metaobjects": {
      "pageInfo": {
        "hasNextPage": false,
        "endCursor": "eyJsYXN0X2lkIjo5NzE2NjI1MzAsImxhc3RfdmFsdWUiOiI5NzE2NjI1MzAifQ=="
      },
      "edges": [
        {
          "node": {
            "handle": "jane-austen",
            "fullName": {
              "jsonValue": "Jane Austen"
            },
            "firstPublished": {
              "jsonValue": 1811
            }
          }
        }
      ]
    }
  }
  ```

* ### Fetch metaobjects with string search

  #### Description

  Fetch the metaobjects entries through a string search.

  #### Query

  ```graphql
  query Metaobjects {
    metaobjects(first: 10, type: "$app:author", query: "fields.full_name:Jane*") {
      nodes {
        handle
        fullName: field(key: "full_name") {
          jsonValue
        }
        firstPublished: field(key: "first_published") {
          jsonValue
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
  "query": "query Metaobjects { metaobjects(first: 10, type: \"$app:author\", query: \"fields.full_name:Jane*\") { nodes { handle fullName: field(key: \"full_name\") { jsonValue } firstPublished: field(key: \"first_published\") { jsonValue } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query Metaobjects {
      metaobjects(first: 10, type: "$app:author", query: "fields.full_name:Jane*") {
        nodes {
          handle
          fullName: field(key: "full_name") {
            jsonValue
          }
          firstPublished: field(key: "first_published") {
            jsonValue
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
    query Metaobjects {
      metaobjects(first: 10, type: "$app:author", query: "fields.full_name:Jane*") {
        nodes {
          handle
          fullName: field(key: "full_name") {
            jsonValue
          }
          firstPublished: field(key: "first_published") {
            jsonValue
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
    data: `query Metaobjects {
      metaobjects(first: 10, type: "$app:author", query: "fields.full_name:Jane*") {
        nodes {
          handle
          fullName: field(key: "full_name") {
            jsonValue
          }
          firstPublished: field(key: "first_published") {
            jsonValue
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
  'query Metaobjects {
    metaobjects(first: 10, type: "$app:author", query: "fields.full_name:Jane*") {
      nodes {
        handle
        fullName: field(key: "full_name") {
          jsonValue
        }
        firstPublished: field(key: "first_published") {
          jsonValue
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "metaobjects": {
      "nodes": [
        {
          "handle": "jane-austen",
          "fullName": {
            "jsonValue": "Jane Austen"
          },
          "firstPublished": {
            "jsonValue": 1811
          }
        }
      ]
    }
  }
  ```
