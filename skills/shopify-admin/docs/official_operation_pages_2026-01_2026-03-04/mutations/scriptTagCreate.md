---
title: scriptTagCreate - GraphQL Admin
description: |-
  <div class="note"><h4>Theme app extensions</h4>
    <p>If your app integrates with a Shopify theme and you plan to submit it to the Shopify App Store, you must use theme app extensions instead of Script tags. Script tags can only be used with vintage themes. <a href="/apps/online-store#what-integration-method-should-i-use" target="_blank">Learn more</a>.</p></div>

  <div class="note"><h4>Script tag deprecation</h4>
    <p>Script tags will be sunset for the <b>Order status</b> page on August 28, 2025. <a href="https://www.shopify.com/plus/upgrading-to-checkout-extensibility">Upgrade to Checkout Extensibility</a> before this date. <a href="/docs/api/liquid/objects#script">Shopify Scripts</a> will continue to work alongside Checkout Extensibility until August 28, 2025.</p></div>


  Creates a new script tag.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/scriptTagCreate'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/scriptTagCreate.md
---

# script​Tag​Create

mutation

Requires `write_script_tags` access scope.

**Theme app extensions:**

If your app integrates with a Shopify theme and you plan to submit it to the Shopify App Store, you must use theme app extensions instead of Script tags. Script tags can only be used with vintage themes. [Learn more](https://shopify.dev/apps/online-store#what-integration-method-should-i-use).

**Script tag deprecation:**

Script tags will be sunset for the **Order status** page on August 28, 2025. [Upgrade to Checkout Extensibility](https://www.shopify.com/plus/upgrading-to-checkout-extensibility) before this date. [Shopify Scripts](https://shopify.dev/docs/api/liquid/objects#script) will continue to work alongside Checkout Extensibility until August 28, 2025.

Creates a new script tag.

## Arguments

* input

  [Script​Tag​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ScriptTagInput)

  required

  The input fields for a script tag.

***

## Script​Tag​Create​Payload returns

* script​Tag

  [Script​Tag](https://shopify.dev/docs/api/admin-graphql/latest/objects/ScriptTag)

  The script tag that was created.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Creates a new script tag

  #### Query

  ```graphql
  mutation ScriptTagCreate($input: ScriptTagInput!) {
    scriptTagCreate(input: $input) {
      scriptTag {
        id
        cache
        createdAt
        displayScope
        src
        updatedAt
      }
      userErrors {
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "src": "https://js.example.org/bar.js",
      "displayScope": "ONLINE_STORE",
      "cache": true
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
  "query": "mutation ScriptTagCreate($input: ScriptTagInput!) { scriptTagCreate(input: $input) { scriptTag { id cache createdAt displayScope src updatedAt } userErrors { field message } } }",
   "variables": {
      "input": {
        "src": "https://js.example.org/bar.js",
        "displayScope": "ONLINE_STORE",
        "cache": true
      }
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
    mutation ScriptTagCreate($input: ScriptTagInput!) {
      scriptTagCreate(input: $input) {
        scriptTag {
          id
          cache
          createdAt
          displayScope
          src
          updatedAt
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "input": {
              "src": "https://js.example.org/bar.js",
              "displayScope": "ONLINE_STORE",
              "cache": true
          }
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
    mutation ScriptTagCreate($input: ScriptTagInput!) {
      scriptTagCreate(input: $input) {
        scriptTag {
          id
          cache
          createdAt
          displayScope
          src
          updatedAt
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "src": "https://js.example.org/bar.js",
      "displayScope": "ONLINE_STORE",
      "cache": true
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation ScriptTagCreate($input: ScriptTagInput!) {
        scriptTagCreate(input: $input) {
          scriptTag {
            id
            cache
            createdAt
            displayScope
            src
            updatedAt
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "src": "https://js.example.org/bar.js",
              "displayScope": "ONLINE_STORE",
              "cache": true
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation ScriptTagCreate($input: ScriptTagInput!) {
    scriptTagCreate(input: $input) {
      scriptTag {
        id
        cache
        createdAt
        displayScope
        src
        updatedAt
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "src": "https://js.example.org/bar.js",
      "displayScope": "ONLINE_STORE",
      "cache": true
    }
  }'
  ```

  #### Response

  ```json
  {
    "scriptTagCreate": {
      "scriptTag": {
        "id": "gid://shopify/ScriptTag/870402687",
        "cache": true,
        "createdAt": "2024-12-18T11:36:28Z",
        "displayScope": "ONLINE_STORE",
        "src": "https://js.example.org/bar.js",
        "updatedAt": "2024-12-18T11:36:28Z"
      },
      "userErrors": []
    }
  }
  ```

* ### scriptTagCreate reference
