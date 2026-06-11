---
title: webPixel - GraphQL Admin
description: >-
  Returns a

  [web
  pixel](https://shopify.dev/docs/apps/build/marketing-analytics/build-web-pixels)

  by ID.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/webPixel'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/webPixel.md'
---

# web​Pixel

query

Returns a [web pixel](https://shopify.dev/docs/apps/build/marketing-analytics/build-web-pixels) by ID.

## Arguments

* id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the `WebPixel` object to return.

***

## Possible returns

* Web​Pixel

  [Web​Pixel](https://shopify.dev/docs/api/admin-graphql/latest/objects/WebPixel)

  The `WebPixel` object enables you to manage JavaScript code snippets that run on an online store and collect [behavioral data](https://shopify.dev/docs/api/web-pixels-api/standard-events) for marketing campaign optimization and analytics.

  Learn how to create a [web pixel extension](https://shopify.dev/docs/apps/build/marketing-analytics/build-web-pixels) to subscribe your app to events that are emitted by Shopify.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * settings

    [JSON!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/JSON)

    non-null

    The [settings object](https://shopify.dev/docs/apps/build/marketing-analytics/build-web-pixels#step-2-define-your-web-pixel-settings) for the web pixel. This object specifies configuration options that control the web pixel's functionality and behavior. You can find the settings for a web pixel in `extensions/<your_extension_name>/shopify.extension.toml`.

***

## Examples

* ### Query a web pixel

  #### Description

  Retrieve a web pixel record on the store where you installed your app. This example shows how to query a web pixel's ID and \[settings object]\(https://shopify.dev/docs/apps/build/marketing-analytics/build-web-pixels#step-2-define-your-web-pixel-settings).

  #### Query

  ```graphql
  query {
    webPixel {
      id
      settings
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
  "query": "query { webPixel { id settings } }"
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
      webPixel {
        id
        settings
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
      webPixel {
        id
        settings
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
      webPixel {
        id
        settings
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    webPixel {
      id
      settings
    }
  }'
  ```

  #### Response

  ```json
  {
    "webPixel": {
      "id": "gid://shopify/WebPixel/845285844",
      "settings": "{foo2: 'bar2'}"
    }
  }
  ```

* ### Query a web pixel by its ID

  #### Description

  Retrieve a \[web pixel]\(https://shopify.dev/docs/apps/build/marketing-analytics/build-web-pixels) record on the store where you installed your app.

  #### Query

  ```graphql
  query {
    webPixel(id: "gid://shopify/WebPixel/845285844") {
      id
      settings
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
  "query": "query { webPixel(id: \"gid://shopify/WebPixel/845285844\") { id settings } }"
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
      webPixel(id: "gid://shopify/WebPixel/845285844") {
        id
        settings
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
      webPixel(id: "gid://shopify/WebPixel/845285844") {
        id
        settings
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
      webPixel(id: "gid://shopify/WebPixel/845285844") {
        id
        settings
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    webPixel(id: "gid://shopify/WebPixel/845285844") {
      id
      settings
    }
  }'
  ```

  #### Response

  ```json
  {
    "webPixel": {
      "id": "gid://shopify/WebPixel/845285844",
      "settings": "{foo2: 'bar2'}"
    }
  }
  ```
