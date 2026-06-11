---
title: webPixelCreate - GraphQL Admin
description: >-
  Activate a [web pixel
  extension](https://shopify.dev/docs/apps/build/marketing-analytics/build-web-pixels)

  by creating a web pixel record on the store where you installed your app.


  When you run the `webPixelCreate` mutation, Shopify validates it

  against the settings definition in `shopify.extension.toml`. If the `settings`
  input field doesn't match

  the schema that you defined, then the mutation fails. Learn how to

  define [web pixel
  settings](https://shopify.dev/docs/apps/build/marketing-analytics/build-web-pixels#step-2-define-your-web-pixel-settings).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/webPixelCreate'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/webPixelCreate.md
---

# web​Pixel​Create

mutation

Requires `write_pixels` access scope. Also: The app requires read\_customer\_events access scope and user access permission.

Activate a [web pixel extension](https://shopify.dev/docs/apps/build/marketing-analytics/build-web-pixels) by creating a web pixel record on the store where you installed your app.

When you run the `webPixelCreate` mutation, Shopify validates it against the settings definition in `shopify.extension.toml`. If the `settings` input field doesn't match the schema that you defined, then the mutation fails. Learn how to define [web pixel settings](https://shopify.dev/docs/apps/build/marketing-analytics/build-web-pixels#step-2-define-your-web-pixel-settings).

## Arguments

* web​Pixel

  [Web​Pixel​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/WebPixelInput)

  required

  The web pixel settings in JSON format.

***

## Web​Pixel​Create​Payload returns

* user​Errors

  [\[Errors​Web​Pixel​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ErrorsWebPixelUserError)

  non-null

  The list of errors that occurred from executing the mutation.

* web​Pixel

  [Web​Pixel](https://shopify.dev/docs/api/admin-graphql/latest/objects/WebPixel)

  The created web pixel settings.

***

## Examples

* ### Create a web pixel

  #### Description

  Create a \[web pixel]\(https://shopify.dev/docs/apps/build/marketing-analytics/build-web-pixels) record on the store where you installed your app. The settings must match the schema defined in your extension's \`shopify.extension.toml\` file.

  #### Query

  ```graphql
  mutation webPixelCreate($webPixel: WebPixelInput!) {
    webPixelCreate(webPixel: $webPixel) {
      userErrors {
        field
        message
        code
      }
      webPixel {
        id
        settings
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "webPixel": {
      "settings": {
        "trackingId": "GA-TRACKING-ID-123"
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
  "query": "mutation webPixelCreate($webPixel: WebPixelInput!) { webPixelCreate(webPixel: $webPixel) { userErrors { field message code } webPixel { id settings } } }",
   "variables": {
      "webPixel": {
        "settings": {
          "trackingId": "GA-TRACKING-ID-123"
        }
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
    mutation webPixelCreate($webPixel: WebPixelInput!) {
      webPixelCreate(webPixel: $webPixel) {
        userErrors {
          field
          message
          code
        }
        webPixel {
          id
          settings
        }
      }
    }`,
    {
      variables: {
          "webPixel": {
              "settings": {
                  "trackingId": "GA-TRACKING-ID-123"
              }
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
    mutation webPixelCreate($webPixel: WebPixelInput!) {
      webPixelCreate(webPixel: $webPixel) {
        userErrors {
          field
          message
          code
        }
        webPixel {
          id
          settings
        }
      }
    }
  QUERY

  variables = {
    "webPixel": {
      "settings": {
        "trackingId": "GA-TRACKING-ID-123"
      }
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation webPixelCreate($webPixel: WebPixelInput!) {
        webPixelCreate(webPixel: $webPixel) {
          userErrors {
            field
            message
            code
          }
          webPixel {
            id
            settings
          }
        }
      }`,
      "variables": {
          "webPixel": {
              "settings": {
                  "trackingId": "GA-TRACKING-ID-123"
              }
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation webPixelCreate($webPixel: WebPixelInput!) {
    webPixelCreate(webPixel: $webPixel) {
      userErrors {
        field
        message
        code
      }
      webPixel {
        id
        settings
      }
    }
  }' \
  --variables \
  '{
    "webPixel": {
      "settings": {
        "trackingId": "GA-TRACKING-ID-123"
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "webPixelCreate": {
      "userErrors": [],
      "webPixel": {
        "id": "gid://shopify/WebPixel/937414752",
        "settings": "{\"trackingId\":\"GA-TRACKING-ID-123\"}"
      }
    }
  }
  ```

* ### Creating a web pixel with invalid settings returns an error

  #### Description

  This example shows the error response when you try to create a web pixel with invalid settings. If you provide an empty \`settings\` object, then the mutation returns an error.

  #### Query

  ```graphql
  mutation webPixelCreate($webPixel: WebPixelInput!) {
    webPixelCreate(webPixel: $webPixel) {
      userErrors {
        field
        message
        code
      }
      webPixel {
        id
        settings
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "webPixel": {
      "settings": {}
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
  "query": "mutation webPixelCreate($webPixel: WebPixelInput!) { webPixelCreate(webPixel: $webPixel) { userErrors { field message code } webPixel { id settings } } }",
   "variables": {
      "webPixel": {
        "settings": {}
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
    mutation webPixelCreate($webPixel: WebPixelInput!) {
      webPixelCreate(webPixel: $webPixel) {
        userErrors {
          field
          message
          code
        }
        webPixel {
          id
          settings
        }
      }
    }`,
    {
      variables: {
          "webPixel": {
              "settings": {}
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
    mutation webPixelCreate($webPixel: WebPixelInput!) {
      webPixelCreate(webPixel: $webPixel) {
        userErrors {
          field
          message
          code
        }
        webPixel {
          id
          settings
        }
      }
    }
  QUERY

  variables = {
    "webPixel": {
      "settings": {}
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation webPixelCreate($webPixel: WebPixelInput!) {
        webPixelCreate(webPixel: $webPixel) {
          userErrors {
            field
            message
            code
          }
          webPixel {
            id
            settings
          }
        }
      }`,
      "variables": {
          "webPixel": {
              "settings": {}
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation webPixelCreate($webPixel: WebPixelInput!) {
    webPixelCreate(webPixel: $webPixel) {
      userErrors {
        field
        message
        code
      }
      webPixel {
        id
        settings
      }
    }
  }' \
  --variables \
  '{
    "webPixel": {
      "settings": {}
    }
  }'
  ```

  #### Response

  ```json
  {
    "webPixelCreate": {
      "userErrors": [
        {
          "field": [
            "webPixel"
          ],
          "message": "Missing keys: trackingId",
          "code": "INVALID_SETTINGS"
        }
      ],
      "webPixel": null
    }
  }
  ```

* ### webPixelCreate reference
