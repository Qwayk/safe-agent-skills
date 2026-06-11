---
title: theme - GraphQL Admin
description: >-
  Returns an
  [`OnlineStoreTheme`](https://shopify.dev/docs/api/admin-graphql/latest/objects/OnlineStoreTheme)
  by its ID. Use this query to retrieve theme metadata and access the theme's
  [`files`](https://shopify.dev/docs/api/admin-graphql/latest/queries/theme#returns-OnlineStoreTheme.fields.files),
  which include templates, assets,
  [translations](https://shopify.dev/docs/api/admin-graphql/latest/objects/OnlineStoreTheme#field-published_translations),
  and configuration files.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/theme'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/theme.md'
---

# theme

query

Requires `read_themes` access scope.

Returns an [`OnlineStoreTheme`](https://shopify.dev/docs/api/admin-graphql/latest/objects/OnlineStoreTheme) by its ID. Use this query to retrieve theme metadata and access the theme's [`files`](https://shopify.dev/docs/api/admin-graphql/latest/queries/theme#returns-OnlineStoreTheme.fields.files), which include templates, assets, [translations](https://shopify.dev/docs/api/admin-graphql/latest/objects/OnlineStoreTheme#field-published_translations), and configuration files.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the theme.

***

## Possible returns

* Online​Store​Theme

  [Online​Store​Theme](https://shopify.dev/docs/api/admin-graphql/latest/objects/OnlineStoreTheme)

  A theme for display on the storefront. Themes control the visual appearance and functionality of the online store through templates, stylesheets, and assets that determine how [products](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product), [collections](https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection), and other content display to customers.

  Each theme has a [role](https://shopify.dev/docs/api/admin-graphql/latest/objects/OnlineStoreTheme#field-OnlineStoreTheme.fields.role) that indicates its status. Main themes are live on the storefront, unpublished themes are inactive, demo themes require purchase before publishing, and development themes are temporary for previewing during development. The theme includes [translations](https://shopify.dev/docs/api/admin-graphql/latest/objects/OnlineStoreTheme#field-OnlineStoreTheme.fields.translations) for multi-language support.

  * created​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the theme was created.

  * files

    [Online​Store​Theme​File​Connection](https://shopify.dev/docs/api/admin-graphql/latest/connections/OnlineStoreThemeFileConnection)

    The files in the theme.

    * filenames

      [\[String!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      ### Arguments

      The filenames of the theme files. At most 50 filenames can be specified. Use '\*' to match zero or more characters.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      Default:50

      Returns at most the first n files for this theme. Fewer than n files may be returned to stay within the payload size limit, or when the end of the list is reached. At most 2500 can be fetched at once.

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      A cursor for use in pagination.

    ***

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The name of the theme, set by the merchant.

  * prefix

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The prefix of the theme.

  * processing

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the theme is processing.

  * processing​Failed

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the theme processing failed.

  * role

    [Theme​Role!](https://shopify.dev/docs/api/admin-graphql/latest/enums/ThemeRole)

    non-null

    The role of the theme.

  * theme​Store​Id

    [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    The theme store ID.

  * translations

    [\[Translation!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Translation)

    non-null

    The published translations associated with the resource.

    * locale

      [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      required

      ### Arguments

      Filters translations locale.

    * market​Id

      [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      Filters translations by market ID. Use this argument to retrieve content specific to a market.

    ***

  * updated​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the theme was last updated.

***

## Examples

* ### Get file content by theme id and filename

  #### Query

  ```graphql
  query {
    theme(id: "gid://shopify/OnlineStoreTheme/225007463") {
      id
      name
      role
      files(filenames: ["assets/index.js"], first: 1) {
        nodes {
          body {
            ... on OnlineStoreThemeFileBodyText {
              content
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
  "query": "query { theme(id: \"gid://shopify/OnlineStoreTheme/225007463\") { id name role files(filenames: [\"assets/index.js\"], first: 1) { nodes { body { ... on OnlineStoreThemeFileBodyText { content } } } } } }"
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
      theme(id: "gid://shopify/OnlineStoreTheme/225007463") {
        id
        name
        role
        files(filenames: ["assets/index.js"], first: 1) {
          nodes {
            body {
              ... on OnlineStoreThemeFileBodyText {
                content
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
      theme(id: "gid://shopify/OnlineStoreTheme/225007463") {
        id
        name
        role
        files(filenames: ["assets/index.js"], first: 1) {
          nodes {
            body {
              ... on OnlineStoreThemeFileBodyText {
                content
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
      theme(id: "gid://shopify/OnlineStoreTheme/225007463") {
        id
        name
        role
        files(filenames: ["assets/index.js"], first: 1) {
          nodes {
            body {
              ... on OnlineStoreThemeFileBodyText {
                content
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
    theme(id: "gid://shopify/OnlineStoreTheme/225007463") {
      id
      name
      role
      files(filenames: ["assets/index.js"], first: 1) {
        nodes {
          body {
            ... on OnlineStoreThemeFileBodyText {
              content
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
    "theme": {
      "id": "gid://shopify/OnlineStoreTheme/225007463",
      "name": "Comfort",
      "role": "UNPUBLISHED",
      "files": {
        "nodes": [
          {
            "body": {
              "content": "console.log('foo');"
            }
          }
        ]
      }
    }
  }
  ```

* ### Get theme by id

  #### Query

  ```graphql
  query {
    theme(id: "gid://shopify/OnlineStoreTheme/529529152") {
      id
      name
      role
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
  "query": "query { theme(id: \"gid://shopify/OnlineStoreTheme/529529152\") { id name role } }"
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
      theme(id: "gid://shopify/OnlineStoreTheme/529529152") {
        id
        name
        role
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
      theme(id: "gid://shopify/OnlineStoreTheme/529529152") {
        id
        name
        role
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
      theme(id: "gid://shopify/OnlineStoreTheme/529529152") {
        id
        name
        role
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    theme(id: "gid://shopify/OnlineStoreTheme/529529152") {
      id
      name
      role
    }
  }'
  ```

  #### Response

  ```json
  {
    "theme": {
      "id": "gid://shopify/OnlineStoreTheme/529529152",
      "name": "Comfort",
      "role": "MAIN"
    }
  }
  ```

* ### Get theme files by theme id

  #### Query

  ```graphql
  query {
    theme(id: "gid://shopify/OnlineStoreTheme/225007463") {
      id
      name
      role
      files {
        edges {
          node {
            filename
            body {
              ... on OnlineStoreThemeFileBodyText {
                content
              }
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
  "query": "query { theme(id: \"gid://shopify/OnlineStoreTheme/225007463\") { id name role files { edges { node { filename body { ... on OnlineStoreThemeFileBodyText { content } } } } } } }"
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
      theme(id: "gid://shopify/OnlineStoreTheme/225007463") {
        id
        name
        role
        files {
          edges {
            node {
              filename
              body {
                ... on OnlineStoreThemeFileBodyText {
                  content
                }
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
      theme(id: "gid://shopify/OnlineStoreTheme/225007463") {
        id
        name
        role
        files {
          edges {
            node {
              filename
              body {
                ... on OnlineStoreThemeFileBodyText {
                  content
                }
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
      theme(id: "gid://shopify/OnlineStoreTheme/225007463") {
        id
        name
        role
        files {
          edges {
            node {
              filename
              body {
                ... on OnlineStoreThemeFileBodyText {
                  content
                }
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
    theme(id: "gid://shopify/OnlineStoreTheme/225007463") {
      id
      name
      role
      files {
        edges {
          node {
            filename
            body {
              ... on OnlineStoreThemeFileBodyText {
                content
              }
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
    "theme": {
      "id": "gid://shopify/OnlineStoreTheme/225007463",
      "name": "Comfort",
      "role": "UNPUBLISHED",
      "files": {
        "edges": [
          {
            "node": {
              "filename": "assets/index.js",
              "body": {
                "content": "console.log('foo');"
              }
            }
          },
          {
            "node": {
              "filename": "assets/styles.css",
              "body": {
                "content": "p { color: red; }"
              }
            }
          },
          {
            "node": {
              "filename": "layout/theme.liquid",
              "body": {
                "content": "<html><head>{{ content_for_header }}</head><body><p>sandbox</p><div>{{ content_for_layout }}</div></body></html>"
              }
            }
          }
        ]
      }
    }
  }
  ```

* ### Retrieves a list of assets for a theme

  #### Query

  ```graphql
  query ThemeFilesPaginated($themeId: ID!) {
    theme(id: $themeId) {
      files(first: 50) {
        edges {
          node {
            body {
              ... on OnlineStoreThemeFileBodyBase64 {
                contentBase64
              }
              ... on OnlineStoreThemeFileBodyText {
                content
              }
              ... on OnlineStoreThemeFileBodyUrl {
                url
              }
            }
            checksumMd5
            contentType
            createdAt
            filename
            size
            updatedAt
          }
          cursor
        }
        pageInfo {
          endCursor
          hasNextPage
          hasPreviousPage
          startCursor
        }
        userErrors {
          code
          filename
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "themeId": "gid://shopify/OnlineStoreTheme/225007463"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query ThemeFilesPaginated($themeId: ID!) { theme(id: $themeId) { files(first: 50) { edges { node { body { ... on OnlineStoreThemeFileBodyBase64 { contentBase64 } ... on OnlineStoreThemeFileBodyText { content } ... on OnlineStoreThemeFileBodyUrl { url } } checksumMd5 contentType createdAt filename size updatedAt } cursor } pageInfo { endCursor hasNextPage hasPreviousPage startCursor } userErrors { code filename } } } }",
   "variables": {
      "themeId": "gid://shopify/OnlineStoreTheme/225007463"
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
    query ThemeFilesPaginated($themeId: ID!) {
      theme(id: $themeId) {
        files(first: 50) {
          edges {
            node {
              body {
                ... on OnlineStoreThemeFileBodyBase64 {
                  contentBase64
                }
                ... on OnlineStoreThemeFileBodyText {
                  content
                }
                ... on OnlineStoreThemeFileBodyUrl {
                  url
                }
              }
              checksumMd5
              contentType
              createdAt
              filename
              size
              updatedAt
            }
            cursor
          }
          pageInfo {
            endCursor
            hasNextPage
            hasPreviousPage
            startCursor
          }
          userErrors {
            code
            filename
          }
        }
      }
    }`,
    {
      variables: {
          "themeId": "gid://shopify/OnlineStoreTheme/225007463"
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
    query ThemeFilesPaginated($themeId: ID!) {
      theme(id: $themeId) {
        files(first: 50) {
          edges {
            node {
              body {
                ... on OnlineStoreThemeFileBodyBase64 {
                  contentBase64
                }
                ... on OnlineStoreThemeFileBodyText {
                  content
                }
                ... on OnlineStoreThemeFileBodyUrl {
                  url
                }
              }
              checksumMd5
              contentType
              createdAt
              filename
              size
              updatedAt
            }
            cursor
          }
          pageInfo {
            endCursor
            hasNextPage
            hasPreviousPage
            startCursor
          }
          userErrors {
            code
            filename
          }
        }
      }
    }
  QUERY

  variables = {
    "themeId": "gid://shopify/OnlineStoreTheme/225007463"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query ThemeFilesPaginated($themeId: ID!) {
        theme(id: $themeId) {
          files(first: 50) {
            edges {
              node {
                body {
                  ... on OnlineStoreThemeFileBodyBase64 {
                    contentBase64
                  }
                  ... on OnlineStoreThemeFileBodyText {
                    content
                  }
                  ... on OnlineStoreThemeFileBodyUrl {
                    url
                  }
                }
                checksumMd5
                contentType
                createdAt
                filename
                size
                updatedAt
              }
              cursor
            }
            pageInfo {
              endCursor
              hasNextPage
              hasPreviousPage
              startCursor
            }
            userErrors {
              code
              filename
            }
          }
        }
      }`,
      "variables": {
          "themeId": "gid://shopify/OnlineStoreTheme/225007463"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query ThemeFilesPaginated($themeId: ID!) {
    theme(id: $themeId) {
      files(first: 50) {
        edges {
          node {
            body {
              ... on OnlineStoreThemeFileBodyBase64 {
                contentBase64
              }
              ... on OnlineStoreThemeFileBodyText {
                content
              }
              ... on OnlineStoreThemeFileBodyUrl {
                url
              }
            }
            checksumMd5
            contentType
            createdAt
            filename
            size
            updatedAt
          }
          cursor
        }
        pageInfo {
          endCursor
          hasNextPage
          hasPreviousPage
          startCursor
        }
        userErrors {
          code
          filename
        }
      }
    }
  }' \
  --variables \
  '{
    "themeId": "gid://shopify/OnlineStoreTheme/225007463"
  }'
  ```

  #### Response

  ```json
  {
    "theme": {
      "files": {
        "edges": [
          {
            "node": {
              "body": {
                "content": "console.log('foo');"
              },
              "checksumMd5": "fd33535a878f593c91bf93c7b39da272",
              "contentType": "application/javascript",
              "createdAt": "2024-10-30T22:18:48Z",
              "filename": "assets/index.js",
              "size": "19",
              "updatedAt": "2024-10-30T22:18:48Z"
            },
            "cursor": "ImFzc2V0c1wvaW5kZXguanMi"
          },
          {
            "node": {
              "body": {
                "content": "p { color: red; }"
              },
              "checksumMd5": "5fc2748b49b0a877ea0bb50a105038ab",
              "contentType": "text/css",
              "createdAt": "2024-10-30T22:18:48Z",
              "filename": "assets/styles.css",
              "size": "17",
              "updatedAt": "2024-10-30T22:18:48Z"
            },
            "cursor": "ImFzc2V0c1wvc3R5bGVzLmNzcyI="
          },
          {
            "node": {
              "body": {
                "content": "<html><head>{{ content_for_header }}</head><body><p>sandbox</p><div>{{ content_for_layout }}</div></body></html>"
              },
              "checksumMd5": null,
              "contentType": "application/x-liquid",
              "createdAt": "2010-07-12T19:31:50Z",
              "filename": "layout/theme.liquid",
              "size": "3252",
              "updatedAt": "2010-07-12T19:31:50Z"
            },
            "cursor": "ImxheW91dFwvdGhlbWUubGlxdWlkIg=="
          }
        ],
        "pageInfo": {
          "endCursor": "ImxheW91dFwvdGhlbWUubGlxdWlkIg==",
          "hasNextPage": false,
          "hasPreviousPage": false,
          "startCursor": "ImFzc2V0c1wvaW5kZXguanMi"
        },
        "userErrors": []
      }
    }
  }
  ```

* ### Retrieves a single asset for a theme

  #### Query

  ```graphql
  query ThemeFiles($themeId: ID!, $filenames: [String!]!) {
    theme(id: $themeId) {
      files(filenames: $filenames) {
        nodes {
          body {
            ... on OnlineStoreThemeFileBodyBase64 {
              contentBase64
            }
            ... on OnlineStoreThemeFileBodyText {
              content
            }
            ... on OnlineStoreThemeFileBodyUrl {
              url
            }
          }
          checksumMd5
          contentType
          createdAt
          filename
          size
          updatedAt
        }
        userErrors {
          code
          filename
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "themeId": "gid://shopify/OnlineStoreTheme/225007463",
    "filenames": [
      "assets/index.js"
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
  "query": "query ThemeFiles($themeId: ID!, $filenames: [String!]!) { theme(id: $themeId) { files(filenames: $filenames) { nodes { body { ... on OnlineStoreThemeFileBodyBase64 { contentBase64 } ... on OnlineStoreThemeFileBodyText { content } ... on OnlineStoreThemeFileBodyUrl { url } } checksumMd5 contentType createdAt filename size updatedAt } userErrors { code filename } } } }",
   "variables": {
      "themeId": "gid://shopify/OnlineStoreTheme/225007463",
      "filenames": [
        "assets/index.js"
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
    query ThemeFiles($themeId: ID!, $filenames: [String!]!) {
      theme(id: $themeId) {
        files(filenames: $filenames) {
          nodes {
            body {
              ... on OnlineStoreThemeFileBodyBase64 {
                contentBase64
              }
              ... on OnlineStoreThemeFileBodyText {
                content
              }
              ... on OnlineStoreThemeFileBodyUrl {
                url
              }
            }
            checksumMd5
            contentType
            createdAt
            filename
            size
            updatedAt
          }
          userErrors {
            code
            filename
          }
        }
      }
    }`,
    {
      variables: {
          "themeId": "gid://shopify/OnlineStoreTheme/225007463",
          "filenames": [
              "assets/index.js"
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
    query ThemeFiles($themeId: ID!, $filenames: [String!]!) {
      theme(id: $themeId) {
        files(filenames: $filenames) {
          nodes {
            body {
              ... on OnlineStoreThemeFileBodyBase64 {
                contentBase64
              }
              ... on OnlineStoreThemeFileBodyText {
                content
              }
              ... on OnlineStoreThemeFileBodyUrl {
                url
              }
            }
            checksumMd5
            contentType
            createdAt
            filename
            size
            updatedAt
          }
          userErrors {
            code
            filename
          }
        }
      }
    }
  QUERY

  variables = {
    "themeId": "gid://shopify/OnlineStoreTheme/225007463",
    "filenames": [
      "assets/index.js"
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query ThemeFiles($themeId: ID!, $filenames: [String!]!) {
        theme(id: $themeId) {
          files(filenames: $filenames) {
            nodes {
              body {
                ... on OnlineStoreThemeFileBodyBase64 {
                  contentBase64
                }
                ... on OnlineStoreThemeFileBodyText {
                  content
                }
                ... on OnlineStoreThemeFileBodyUrl {
                  url
                }
              }
              checksumMd5
              contentType
              createdAt
              filename
              size
              updatedAt
            }
            userErrors {
              code
              filename
            }
          }
        }
      }`,
      "variables": {
          "themeId": "gid://shopify/OnlineStoreTheme/225007463",
          "filenames": [
              "assets/index.js"
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query ThemeFiles($themeId: ID!, $filenames: [String!]!) {
    theme(id: $themeId) {
      files(filenames: $filenames) {
        nodes {
          body {
            ... on OnlineStoreThemeFileBodyBase64 {
              contentBase64
            }
            ... on OnlineStoreThemeFileBodyText {
              content
            }
            ... on OnlineStoreThemeFileBodyUrl {
              url
            }
          }
          checksumMd5
          contentType
          createdAt
          filename
          size
          updatedAt
        }
        userErrors {
          code
          filename
        }
      }
    }
  }' \
  --variables \
  '{
    "themeId": "gid://shopify/OnlineStoreTheme/225007463",
    "filenames": [
      "assets/index.js"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "theme": {
      "files": {
        "nodes": [
          {
            "body": {
              "content": "console.log('foo');"
            },
            "checksumMd5": "fd33535a878f593c91bf93c7b39da272",
            "contentType": "application/javascript",
            "createdAt": "2024-10-30T22:18:46Z",
            "filename": "assets/index.js",
            "size": "19",
            "updatedAt": "2024-10-30T22:18:46Z"
          }
        ],
        "userErrors": []
      }
    }
  }
  ```

* ### Retrieves a single theme by its ID

  #### Query

  ```graphql
  query Theme($id: ID!) {
    theme(id: $id) {
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
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/OnlineStoreTheme/529529152"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query Theme($id: ID!) { theme(id: $id) { createdAt id name prefix processing processingFailed role themeStoreId updatedAt } }",
   "variables": {
      "id": "gid://shopify/OnlineStoreTheme/529529152"
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
    query Theme($id: ID!) {
      theme(id: $id) {
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
    }`,
    {
      variables: {
          "id": "gid://shopify/OnlineStoreTheme/529529152"
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
    query Theme($id: ID!) {
      theme(id: $id) {
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
    }
  QUERY

  variables = {
    "id": "gid://shopify/OnlineStoreTheme/529529152"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query Theme($id: ID!) {
        theme(id: $id) {
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
      }`,
      "variables": {
          "id": "gid://shopify/OnlineStoreTheme/529529152"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query Theme($id: ID!) {
    theme(id: $id) {
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
  }' \
  --variables \
  '{
    "id": "gid://shopify/OnlineStoreTheme/529529152"
  }'
  ```

  #### Response

  ```json
  {
    "theme": {
      "createdAt": "2024-10-30T22:18:09Z",
      "id": "gid://shopify/OnlineStoreTheme/529529152",
      "name": "Comfort",
      "prefix": "/t/1",
      "processing": false,
      "processingFailed": false,
      "role": "MAIN",
      "themeStoreId": 1234,
      "updatedAt": "2024-10-30T22:18:09Z"
    }
  }
  ```
