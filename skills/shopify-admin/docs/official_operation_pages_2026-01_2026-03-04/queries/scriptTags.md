---
title: scriptTags - GraphQL Admin
description: |-
  <div class="note"><h4>Theme app extensions</h4>
    <p>If your app integrates with a Shopify theme and you plan to submit it to the Shopify App Store, you must use theme app extensions instead of Script tags. Script tags can only be used with vintage themes. <a href="/apps/online-store#what-integration-method-should-i-use" target="_blank">Learn more</a>.</p></div>

  <div class="note"><h4>Script tag deprecation</h4>
    <p>Script tags will be sunset for the <b>Order status</b> page on August 28, 2025. <a href="https://www.shopify.com/plus/upgrading-to-checkout-extensibility">Upgrade to Checkout Extensibility</a> before this date. <a href="/docs/api/liquid/objects#script">Shopify Scripts</a> will continue to work alongside Checkout Extensibility until August 28, 2025.</p></div>


  A list of script tags.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/scriptTags'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/scriptTags.md'
---

# script​Tags

query

**Theme app extensions:**

If your app integrates with a Shopify theme and you plan to submit it to the Shopify App Store, you must use theme app extensions instead of Script tags. Script tags can only be used with vintage themes. [Learn more](https://shopify.dev/apps/online-store#what-integration-method-should-i-use).

**Script tag deprecation:**

Script tags will be sunset for the **Order status** page on August 28, 2025. [Upgrade to Checkout Extensibility](https://www.shopify.com/plus/upgrading-to-checkout-extensibility) before this date. [Shopify Scripts](https://shopify.dev/docs/api/liquid/objects#script) will continue to work alongside Checkout Extensibility until August 28, 2025.

A list of script tags.

## ScriptTagConnection arguments

[ScriptTagConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ScriptTagConnection)

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

    * src

      string

    - Filter by `id` range.

    - Example:
      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

  * updated\_at

    time

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* src

  [URL](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

  The source URL of the script tag to filter by.

***

## Possible returns

* edges

  [\[Script​Tag​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ScriptTagEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Script​Tag!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ScriptTag)

  non-null

  A list of nodes that are contained in ScriptTagEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Get the first five script tags

  #### Description

  The following query retrieves the ID of the first five script tags for a shop.

  #### Query

  ```graphql
  query {
    scriptTags(first: 5) {
      edges {
        node {
          id
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
  "query": "query { scriptTags(first: 5) { edges { node { id } } } }"
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
      scriptTags(first: 5) {
        edges {
          node {
            id
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
      scriptTags(first: 5) {
        edges {
          node {
            id
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
      scriptTags(first: 5) {
        edges {
          node {
            id
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
    scriptTags(first: 5) {
      edges {
        node {
          id
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "scriptTags": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/ScriptTag/193372190"
          }
        },
        {
          "node": {
            "id": "gid://shopify/ScriptTag/408148298"
          }
        },
        {
          "node": {
            "id": "gid://shopify/ScriptTag/466217408"
          }
        },
        {
          "node": {
            "id": "gid://shopify/ScriptTag/558170166"
          }
        },
        {
          "node": {
            "id": "gid://shopify/ScriptTag/764371933"
          }
        }
      ]
    }
  }
  ```

* ### Get the first script tag with a specific source URL

  #### Description

  The following query retrieves the ID of the first script tag for a shop with a specific source URL.

  #### Query

  ```graphql
  query {
    scriptTags(first: 1, src: "https://js.example.org/foo.js") {
      edges {
        node {
          id
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
  "query": "query { scriptTags(first: 1, src: \"https://js.example.org/foo.js\") { edges { node { id } } } }"
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
      scriptTags(first: 1, src: "https://js.example.org/foo.js") {
        edges {
          node {
            id
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
      scriptTags(first: 1, src: "https://js.example.org/foo.js") {
        edges {
          node {
            id
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
      scriptTags(first: 1, src: "https://js.example.org/foo.js") {
        edges {
          node {
            id
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
    scriptTags(first: 1, src: "https://js.example.org/foo.js") {
      edges {
        node {
          id
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "scriptTags": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/ScriptTag/466217408"
          }
        }
      ]
    }
  }
  ```

* ### Retrieves a list of all script tags

  #### Query

  ```graphql
  query GetScriptTags($first: Int!, $cursor: String) {
    scriptTags(first: $first, after: $cursor) {
      nodes {
        id
        cache
        createdAt
        displayScope
        src
        updatedAt
      }
      pageInfo {
        startCursor
        endCursor
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "first": 5,
    "cursor": null
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query GetScriptTags($first: Int!, $cursor: String) { scriptTags(first: $first, after: $cursor) { nodes { id cache createdAt displayScope src updatedAt } pageInfo { startCursor endCursor } } }",
   "variables": {
      "first": 5,
      "cursor": null
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
    query GetScriptTags($first: Int!, $cursor: String) {
      scriptTags(first: $first, after: $cursor) {
        nodes {
          id
          cache
          createdAt
          displayScope
          src
          updatedAt
        }
        pageInfo {
          startCursor
          endCursor
        }
      }
    }`,
    {
      variables: {
          "first": 5,
          "cursor": null
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
    query GetScriptTags($first: Int!, $cursor: String) {
      scriptTags(first: $first, after: $cursor) {
        nodes {
          id
          cache
          createdAt
          displayScope
          src
          updatedAt
        }
        pageInfo {
          startCursor
          endCursor
        }
      }
    }
  QUERY

  variables = {
    "first": 5,
    "cursor": null
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query GetScriptTags($first: Int!, $cursor: String) {
        scriptTags(first: $first, after: $cursor) {
          nodes {
            id
            cache
            createdAt
            displayScope
            src
            updatedAt
          }
          pageInfo {
            startCursor
            endCursor
          }
        }
      }`,
      "variables": {
          "first": 5,
          "cursor": null
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query GetScriptTags($first: Int!, $cursor: String) {
    scriptTags(first: $first, after: $cursor) {
      nodes {
        id
        cache
        createdAt
        displayScope
        src
        updatedAt
      }
      pageInfo {
        startCursor
        endCursor
      }
    }
  }' \
  --variables \
  '{
    "first": 5,
    "cursor": null
  }'
  ```

  #### Response

  ```json
  {
    "scriptTags": {
      "nodes": [
        {
          "id": "gid://shopify/ScriptTag/193372190",
          "cache": false,
          "createdAt": "2024-10-29T22:38:08Z",
          "displayScope": "ONLINE_STORE",
          "src": "https://js.example.org/online_store.js",
          "updatedAt": "2024-10-29T22:38:08Z"
        },
        {
          "id": "gid://shopify/ScriptTag/408148298",
          "cache": false,
          "createdAt": "2024-10-29T22:38:08Z",
          "displayScope": "ALL",
          "src": "https://protocol-relative.com/foo.js",
          "updatedAt": "2024-10-29T22:38:08Z"
        },
        {
          "id": "gid://shopify/ScriptTag/466217408",
          "cache": false,
          "createdAt": "2024-10-29T22:38:08Z",
          "displayScope": "ALL",
          "src": "https://js.example.org/foo.js",
          "updatedAt": "2024-10-29T22:38:08Z"
        },
        {
          "id": "gid://shopify/ScriptTag/558170166",
          "cache": false,
          "createdAt": "2024-10-29T22:38:08Z",
          "displayScope": "ALL",
          "src": "https://js.example.org/bar.js?bar=baz",
          "updatedAt": "2024-10-29T22:38:08Z"
        },
        {
          "id": "gid://shopify/ScriptTag/764371933",
          "cache": false,
          "createdAt": "2024-10-29T22:38:08Z",
          "displayScope": "ALL",
          "src": "https://secure-js.example.org/bar.js?bar=baz",
          "updatedAt": "2024-10-29T22:38:08Z"
        }
      ],
      "pageInfo": {
        "startCursor": "eyJsYXN0X2lkIjoxOTMzNzIxOTAsImxhc3RfdmFsdWUiOiIxOTMzNzIxOTAifQ==",
        "endCursor": "eyJsYXN0X2lkIjo3NjQzNzE5MzMsImxhc3RfdmFsdWUiOiI3NjQzNzE5MzMifQ=="
      }
    }
  }
  ```
