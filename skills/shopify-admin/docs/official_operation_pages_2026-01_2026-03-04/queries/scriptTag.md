---
title: scriptTag - GraphQL Admin
description: |-
  <div class="note"><h4>Theme app extensions</h4>
    <p>If your app integrates with a Shopify theme and you plan to submit it to the Shopify App Store, you must use theme app extensions instead of Script tags. Script tags can only be used with vintage themes. <a href="/apps/online-store#what-integration-method-should-i-use" target="_blank">Learn more</a>.</p></div>

  <div class="note"><h4>Script tag deprecation</h4>
    <p>Script tags will be sunset for the <b>Order status</b> page on August 28, 2025. <a href="https://www.shopify.com/plus/upgrading-to-checkout-extensibility">Upgrade to Checkout Extensibility</a> before this date. <a href="/docs/api/liquid/objects#script">Shopify Scripts</a> will continue to work alongside Checkout Extensibility until August 28, 2025.</p></div>


  Returns a `ScriptTag` resource by ID.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/scriptTag'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/scriptTag.md'
---

# script​Tag

query

**Theme app extensions:**

If your app integrates with a Shopify theme and you plan to submit it to the Shopify App Store, you must use theme app extensions instead of Script tags. Script tags can only be used with vintage themes. [Learn more](https://shopify.dev/apps/online-store#what-integration-method-should-i-use).

**Script tag deprecation:**

Script tags will be sunset for the **Order status** page on August 28, 2025. [Upgrade to Checkout Extensibility](https://www.shopify.com/plus/upgrading-to-checkout-extensibility) before this date. [Shopify Scripts](https://shopify.dev/docs/api/liquid/objects#script) will continue to work alongside Checkout Extensibility until August 28, 2025.

Returns a `ScriptTag` resource by ID.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the `ScriptTag` to return.

***

## Possible returns

* Script​Tag

  [Script​Tag](https://shopify.dev/docs/api/admin-graphql/latest/objects/ScriptTag)

  **Theme app extensions:**

  If your app integrates with a Shopify theme and you plan to submit it to the Shopify App Store, you must use theme app extensions instead of Script tags. Script tags can only be used with vintage themes. [Learn more](https://shopify.dev/apps/online-store#what-integration-method-should-i-use).

  **Script tag deprecation:**

  Script tags will be sunset for the **Order status** page on August 28, 2025. [Upgrade to Checkout Extensibility](https://www.shopify.com/plus/upgrading-to-checkout-extensibility) before this date. [Shopify Scripts](https://shopify.dev/docs/api/liquid/objects#script) will continue to work alongside Checkout Extensibility until August 28, 2025.

  A script tag represents remote JavaScript code that is loaded into the pages of a shop's storefront or the **Order status** page of checkout.

  * cache

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the Shopify CDN can cache and serve the script tag. If `true`, then the script will be cached and served by the CDN. The cache expires 15 minutes after the script tag is successfully returned. If `false`, then the script will be served as is.

  * created​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the script tag was created.

  * display​Scope

    [Script​Tag​Display​Scope!](https://shopify.dev/docs/api/admin-graphql/latest/enums/ScriptTagDisplayScope)

    non-null

    The page or pages on the online store that the script should be included.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * legacy​Resource​Id

    [Unsigned​Int64!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/UnsignedInt64)

    non-null

    The ID of the corresponding resource in the REST Admin API.

  * src

    [URL!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    non-null

    The URL to the remote script.

  * updated​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the script tag was last updated.

***

## Examples

* ### Retrieves a single script tag

  #### Query

  ```graphql
  query GetScriptTag($id: ID!) {
    scriptTag(id: $id) {
      id
      cache
      createdAt
      displayScope
      src
      updatedAt
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/ScriptTag/466217408"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query GetScriptTag($id: ID!) { scriptTag(id: $id) { id cache createdAt displayScope src updatedAt } }",
   "variables": {
      "id": "gid://shopify/ScriptTag/466217408"
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
    query GetScriptTag($id: ID!) {
      scriptTag(id: $id) {
        id
        cache
        createdAt
        displayScope
        src
        updatedAt
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/ScriptTag/466217408"
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
    query GetScriptTag($id: ID!) {
      scriptTag(id: $id) {
        id
        cache
        createdAt
        displayScope
        src
        updatedAt
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/ScriptTag/466217408"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query GetScriptTag($id: ID!) {
        scriptTag(id: $id) {
          id
          cache
          createdAt
          displayScope
          src
          updatedAt
        }
      }`,
      "variables": {
          "id": "gid://shopify/ScriptTag/466217408"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query GetScriptTag($id: ID!) {
    scriptTag(id: $id) {
      id
      cache
      createdAt
      displayScope
      src
      updatedAt
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/ScriptTag/466217408"
  }'
  ```

  #### Response

  ```json
  {
    "scriptTag": {
      "id": "gid://shopify/ScriptTag/466217408",
      "cache": false,
      "createdAt": "2024-10-29T22:38:08Z",
      "displayScope": "ALL",
      "src": "https://js.example.org/foo.js",
      "updatedAt": "2024-10-29T22:38:08Z"
    }
  }
  ```
