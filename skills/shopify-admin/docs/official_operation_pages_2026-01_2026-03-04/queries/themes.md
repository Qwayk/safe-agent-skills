---
title: themes - GraphQL Admin
description: >-
  Returns a paginated list of
  [`OnlineStoreTheme`](https://shopify.dev/docs/api/admin-graphql/latest/objects/OnlineStoreTheme)
  objects for the online store. Themes control the appearance and layout of the
  storefront.


  You can filter themes by
  [`role`](https://shopify.dev/docs/api/admin-graphql/latest/queries/themes#arguments-roles)
  to find specific theme types, such as `MAIN` for the published theme and
  `UNPUBLISHED` for draft themes.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/themes'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/themes.md'
---

# themes

query

Requires `read_themes` access scope.

Returns a paginated list of [`OnlineStoreTheme`](https://shopify.dev/docs/api/admin-graphql/latest/objects/OnlineStoreTheme) objects for the online store. Themes control the appearance and layout of the storefront.

You can filter themes by [`role`](https://shopify.dev/docs/api/admin-graphql/latest/queries/themes#arguments-roles) to find specific theme types, such as `MAIN` for the published theme and `UNPUBLISHED` for draft themes.

## OnlineStoreThemeConnection arguments

[OnlineStoreThemeConnection](https://shopify.dev/docs/api/admin-graphql/latest/connections/OnlineStoreThemeConnection)

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

* names

  [\[String!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The theme names to filter by. Use '\*' to match zero or more characters.

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* roles

  [\[Theme​Role!\]](https://shopify.dev/docs/api/admin-graphql/latest/enums/ThemeRole)

  The theme roles to filter by.

***

## Possible returns

* edges

  [\[Online​Store​Theme​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/OnlineStoreThemeEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Online​Store​Theme!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/OnlineStoreTheme)

  non-null

  A list of nodes that are contained in OnlineStoreThemeEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Get first theme

  #### Query

  ```graphql
  query {
    themes(first: 1) {
      edges {
        node {
          name
          id
          role
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
  "query": "query { themes(first: 1) { edges { node { name id role } } } }"
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
      themes(first: 1) {
        edges {
          node {
            name
            id
            role
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
      themes(first: 1) {
        edges {
          node {
            name
            id
            role
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
      themes(first: 1) {
        edges {
          node {
            name
            id
            role
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
    themes(first: 1) {
      edges {
        node {
          name
          id
          role
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "themes": {
      "edges": [
        {
          "node": {
            "name": "main",
            "id": "gid://shopify/OnlineStoreTheme/672824141",
            "role": "MAIN"
          }
        }
      ]
    }
  }
  ```

* ### Get themes by name

  #### Query

  ```graphql
  query {
    themes(first: 10, names: ["Com*", "Development"]) {
      nodes {
        id
        name
        role
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
  "query": "query { themes(first: 10, names: [\"Com*\", \"Development\"]) { nodes { id name role } } }"
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
      themes(first: 10, names: ["Com*", "Development"]) {
        nodes {
          id
          name
          role
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
      themes(first: 10, names: ["Com*", "Development"]) {
        nodes {
          id
          name
          role
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
      themes(first: 10, names: ["Com*", "Development"]) {
        nodes {
          id
          name
          role
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
    themes(first: 10, names: ["Com*", "Development"]) {
      nodes {
        id
        name
        role
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "themes": {
      "nodes": [
        {
          "id": "gid://shopify/OnlineStoreTheme/225007463",
          "name": "Comfort",
          "role": "UNPUBLISHED"
        },
        {
          "id": "gid://shopify/OnlineStoreTheme/273775728",
          "name": "Development",
          "role": "DEVELOPMENT"
        },
        {
          "id": "gid://shopify/OnlineStoreTheme/529529152",
          "name": "Comfort",
          "role": "MAIN"
        },
        {
          "id": "gid://shopify/OnlineStoreTheme/756912091",
          "name": "Comfort Copy",
          "role": "UNPUBLISHED"
        }
      ]
    }
  }
  ```

* ### Retrieves a list of themes

  #### Query

  ```graphql
  query ThemeList {
    themes(first: 10) {
      edges {
        node {
          createdAt
          id
          name
          prefix
          processing
          processingFailed
          role
          themeStoreId
          updatedAt
        }
        cursor
      }
      pageInfo {
        hasNextPage
        hasPreviousPage
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
  "query": "query ThemeList { themes(first: 10) { edges { node { createdAt id name prefix processing processingFailed role themeStoreId updatedAt } cursor } pageInfo { hasNextPage hasPreviousPage } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query ThemeList {
      themes(first: 10) {
        edges {
          node {
            createdAt
            id
            name
            prefix
            processing
            processingFailed
            role
            themeStoreId
            updatedAt
          }
          cursor
        }
        pageInfo {
          hasNextPage
          hasPreviousPage
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
    query ThemeList {
      themes(first: 10) {
        edges {
          node {
            createdAt
            id
            name
            prefix
            processing
            processingFailed
            role
            themeStoreId
            updatedAt
          }
          cursor
        }
        pageInfo {
          hasNextPage
          hasPreviousPage
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
    data: `query ThemeList {
      themes(first: 10) {
        edges {
          node {
            createdAt
            id
            name
            prefix
            processing
            processingFailed
            role
            themeStoreId
            updatedAt
          }
          cursor
        }
        pageInfo {
          hasNextPage
          hasPreviousPage
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query ThemeList {
    themes(first: 10) {
      edges {
        node {
          createdAt
          id
          name
          prefix
          processing
          processingFailed
          role
          themeStoreId
          updatedAt
        }
        cursor
      }
      pageInfo {
        hasNextPage
        hasPreviousPage
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "themes": {
      "edges": [
        {
          "node": {
            "createdAt": "2024-10-30T22:18:09Z",
            "id": "gid://shopify/OnlineStoreTheme/69265273",
            "name": "Blockified",
            "prefix": "/t/5",
            "processing": false,
            "processingFailed": false,
            "role": "UNPUBLISHED",
            "themeStoreId": null,
            "updatedAt": "2024-10-30T22:18:09Z"
          },
          "cursor": "eyJsYXN0X2lkIjo2OTI2NTI3MywibGFzdF92YWx1ZSI6NjkyNjUyNzN9"
        },
        {
          "node": {
            "createdAt": "2024-10-30T22:18:09Z",
            "id": "gid://shopify/OnlineStoreTheme/225007463",
            "name": "Comfort",
            "prefix": "/t/10",
            "processing": false,
            "processingFailed": false,
            "role": "UNPUBLISHED",
            "themeStoreId": 1234,
            "updatedAt": "2024-10-30T22:18:09Z"
          },
          "cursor": "eyJsYXN0X2lkIjoyMjUwMDc0NjMsImxhc3RfdmFsdWUiOjIyNTAwNzQ2M30="
        },
        {
          "node": {
            "createdAt": "2024-10-30T22:18:09Z",
            "id": "gid://shopify/OnlineStoreTheme/273775728",
            "name": "Development",
            "prefix": "/t/8",
            "processing": false,
            "processingFailed": false,
            "role": "DEVELOPMENT",
            "themeStoreId": null,
            "updatedAt": "2024-10-30T22:18:09Z"
          },
          "cursor": "eyJsYXN0X2lkIjoyNzM3NzU3MjgsImxhc3RfdmFsdWUiOjI3Mzc3NTcyOH0="
        },
        {
          "node": {
            "createdAt": "2024-10-30T22:18:09Z",
            "id": "gid://shopify/OnlineStoreTheme/486964194",
            "name": "Legacy",
            "prefix": "/t/4",
            "processing": false,
            "processingFailed": false,
            "role": "UNPUBLISHED",
            "themeStoreId": 12,
            "updatedAt": "2024-10-30T22:18:09Z"
          },
          "cursor": "eyJsYXN0X2lkIjo0ODY5NjQxOTQsImxhc3RfdmFsdWUiOjQ4Njk2NDE5NH0="
        },
        {
          "node": {
            "createdAt": "2024-10-30T22:18:09Z",
            "id": "gid://shopify/OnlineStoreTheme/529529152",
            "name": "Comfort",
            "prefix": "/t/1",
            "processing": false,
            "processingFailed": false,
            "role": "MAIN",
            "themeStoreId": 1234,
            "updatedAt": "2024-10-30T22:18:09Z"
          },
          "cursor": "eyJsYXN0X2lkIjo1Mjk1MjkxNTIsImxhc3RfdmFsdWUiOjUyOTUyOTE1Mn0="
        },
        {
          "node": {
            "createdAt": "2024-10-30T22:18:09Z",
            "id": "gid://shopify/OnlineStoreTheme/535899345",
            "name": "Internationalized",
            "prefix": "/t/6",
            "processing": false,
            "processingFailed": false,
            "role": "UNPUBLISHED",
            "themeStoreId": null,
            "updatedAt": "2024-10-30T22:18:09Z"
          },
          "cursor": "eyJsYXN0X2lkIjo1MzU4OTkzNDUsImxhc3RfdmFsdWUiOjUzNTg5OTM0NX0="
        },
        {
          "node": {
            "createdAt": "2024-10-30T22:18:09Z",
            "id": "gid://shopify/OnlineStoreTheme/756912091",
            "name": "Comfort Copy",
            "prefix": "/t/9",
            "processing": false,
            "processingFailed": false,
            "role": "UNPUBLISHED",
            "themeStoreId": 12345,
            "updatedAt": "2024-10-30T22:18:09Z"
          },
          "cursor": "eyJsYXN0X2lkIjo3NTY5MTIwOTEsImxhc3RfdmFsdWUiOjc1NjkxMjA5MX0="
        },
        {
          "node": {
            "createdAt": "2024-10-30T22:18:09Z",
            "id": "gid://shopify/OnlineStoreTheme/908009861",
            "name": "Sandbox",
            "prefix": "/t/3",
            "processing": false,
            "processingFailed": false,
            "role": "UNPUBLISHED",
            "themeStoreId": 1234,
            "updatedAt": "2024-10-30T22:18:09Z"
          },
          "cursor": "eyJsYXN0X2lkIjo5MDgwMDk4NjEsImxhc3RfdmFsdWUiOjkwODAwOTg2MX0="
        },
        {
          "node": {
            "createdAt": "2024-10-30T22:18:09Z",
            "id": "gid://shopify/OnlineStoreTheme/918442480",
            "name": "Speed",
            "prefix": "/t/2",
            "processing": false,
            "processingFailed": false,
            "role": "MOBILE",
            "themeStoreId": null,
            "updatedAt": "2024-10-30T22:18:09Z"
          },
          "cursor": "eyJsYXN0X2lkIjo5MTg0NDI0ODAsImxhc3RfdmFsdWUiOjkxODQ0MjQ4MH0="
        }
      ],
      "pageInfo": {
        "hasNextPage": false,
        "hasPreviousPage": false
      }
    }
  }
  ```
