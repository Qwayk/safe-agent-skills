---
title: storefrontAccessTokenCreate - GraphQL Admin
description: >-
  Creates a storefront access token that delegates unauthenticated access scopes
  to clients using the [Storefront
  API](https://shopify.dev/docs/api/storefront). The token provides public
  access to storefront resources without requiring customer authentication.


  Each shop can have up to 100 active
  [`StorefrontAccessToken`](https://shopify.dev/docs/api/admin-graphql/latest/objects/StorefrontAccessToken)
  objects. Headless storefronts, mobile apps, and other client applications
  typically use these tokens to access public storefront data.


  Learn more about [building with the Storefront
  API](https://shopify.dev/docs/storefronts/headless/building-with-the-storefront-api/getting-started).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/storefrontAccessTokenCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/storefrontAccessTokenCreate.md
---

# storefront​Access​Token​Create

mutation

Creates a storefront access token that delegates unauthenticated access scopes to clients using the [Storefront API](https://shopify.dev/docs/api/storefront). The token provides public access to storefront resources without requiring customer authentication.

Each shop can have up to 100 active [`StorefrontAccessToken`](https://shopify.dev/docs/api/admin-graphql/latest/objects/StorefrontAccessToken) objects. Headless storefronts, mobile apps, and other client applications typically use these tokens to access public storefront data.

Learn more about [building with the Storefront API](https://shopify.dev/docs/storefronts/headless/building-with-the-storefront-api/getting-started).

## Arguments

* input

  [Storefront​Access​Token​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/StorefrontAccessTokenInput)

  required

  Provides the input fields for creating a storefront access token.

***

## Storefront​Access​Token​Create​Payload returns

* shop

  [Shop!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Shop)

  non-null

  The user's shop.

* storefront​Access​Token

  [Storefront​Access​Token](https://shopify.dev/docs/api/admin-graphql/latest/objects/StorefrontAccessToken)

  The storefront access token.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a Storefront Access Token

  #### Description

  This example demonstrates how to create a storefront access token.

  #### Query

  ```graphql
  mutation StorefrontAccessTokenCreate($input: StorefrontAccessTokenInput!) {
    storefrontAccessTokenCreate(input: $input) {
      userErrors {
        field
        message
      }
      shop {
        id
      }
      storefrontAccessToken {
        accessScopes {
          handle
        }
        accessToken
        title
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "title": "New Storefront Access Token"
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
  "query": "mutation StorefrontAccessTokenCreate($input: StorefrontAccessTokenInput!) { storefrontAccessTokenCreate(input: $input) { userErrors { field message } shop { id } storefrontAccessToken { accessScopes { handle } accessToken title } } }",
   "variables": {
      "input": {
        "title": "New Storefront Access Token"
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
    mutation StorefrontAccessTokenCreate($input: StorefrontAccessTokenInput!) {
      storefrontAccessTokenCreate(input: $input) {
        userErrors {
          field
          message
        }
        shop {
          id
        }
        storefrontAccessToken {
          accessScopes {
            handle
          }
          accessToken
          title
        }
      }
    }`,
    {
      variables: {
          "input": {
              "title": "New Storefront Access Token"
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
    mutation StorefrontAccessTokenCreate($input: StorefrontAccessTokenInput!) {
      storefrontAccessTokenCreate(input: $input) {
        userErrors {
          field
          message
        }
        shop {
          id
        }
        storefrontAccessToken {
          accessScopes {
            handle
          }
          accessToken
          title
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "title": "New Storefront Access Token"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation StorefrontAccessTokenCreate($input: StorefrontAccessTokenInput!) {
        storefrontAccessTokenCreate(input: $input) {
          userErrors {
            field
            message
          }
          shop {
            id
          }
          storefrontAccessToken {
            accessScopes {
              handle
            }
            accessToken
            title
          }
        }
      }`,
      "variables": {
          "input": {
              "title": "New Storefront Access Token"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation StorefrontAccessTokenCreate($input: StorefrontAccessTokenInput!) {
    storefrontAccessTokenCreate(input: $input) {
      userErrors {
        field
        message
      }
      shop {
        id
      }
      storefrontAccessToken {
        accessScopes {
          handle
        }
        accessToken
        title
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "title": "New Storefront Access Token"
    }
  }'
  ```

  #### Response

  ```json
  {
    "storefrontAccessTokenCreate": {
      "userErrors": [],
      "shop": {
        "id": "gid://shopify/Shop/325953821"
      },
      "storefrontAccessToken": {
        "accessScopes": [
          {
            "handle": "unauthenticated_read_product_listings"
          },
          {
            "handle": "unauthenticated_write_checkouts"
          },
          {
            "handle": "unauthenticated_read_checkouts"
          },
          {
            "handle": "unauthenticated_read_selling_plans"
          }
        ],
        "accessToken": "d016c3f69af5f85abdcd3b3252469efc",
        "title": "New Storefront Access Token"
      }
    }
  }
  ```

* ### Creates a new StorefrontAccessToken

  #### Query

  ```graphql
  mutation storeFrontAccessTokenCreate($input: StorefrontAccessTokenInput!) {
    storefrontAccessTokenCreate(input: $input) {
      storefrontAccessToken {
        id
        accessToken
        accessScopes {
          handle
        }
        createdAt
        title
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
      "title": "New Storefront Access Token"
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
  "query": "mutation storeFrontAccessTokenCreate($input: StorefrontAccessTokenInput!) { storefrontAccessTokenCreate(input: $input) { storefrontAccessToken { id accessToken accessScopes { handle } createdAt title } userErrors { field message } } }",
   "variables": {
      "input": {
        "title": "New Storefront Access Token"
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
    mutation storeFrontAccessTokenCreate($input: StorefrontAccessTokenInput!) {
      storefrontAccessTokenCreate(input: $input) {
        storefrontAccessToken {
          id
          accessToken
          accessScopes {
            handle
          }
          createdAt
          title
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
              "title": "New Storefront Access Token"
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
    mutation storeFrontAccessTokenCreate($input: StorefrontAccessTokenInput!) {
      storefrontAccessTokenCreate(input: $input) {
        storefrontAccessToken {
          id
          accessToken
          accessScopes {
            handle
          }
          createdAt
          title
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
      "title": "New Storefront Access Token"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation storeFrontAccessTokenCreate($input: StorefrontAccessTokenInput!) {
        storefrontAccessTokenCreate(input: $input) {
          storefrontAccessToken {
            id
            accessToken
            accessScopes {
              handle
            }
            createdAt
            title
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "title": "New Storefront Access Token"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation storeFrontAccessTokenCreate($input: StorefrontAccessTokenInput!) {
    storefrontAccessTokenCreate(input: $input) {
      storefrontAccessToken {
        id
        accessToken
        accessScopes {
          handle
        }
        createdAt
        title
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
      "title": "New Storefront Access Token"
    }
  }'
  ```

  #### Response

  ```json
  {
    "storefrontAccessTokenCreate": {
      "storefrontAccessToken": {
        "id": "gid://shopify/StorefrontAccessToken/1003303992",
        "accessToken": "2a1753b19c85ac630f27391da802765d",
        "accessScopes": [
          {
            "handle": "unauthenticated_read_product_listings"
          },
          {
            "handle": "unauthenticated_write_checkouts"
          },
          {
            "handle": "unauthenticated_read_checkouts"
          },
          {
            "handle": "unauthenticated_read_selling_plans"
          }
        ],
        "createdAt": "2024-10-29T18:54:07Z",
        "title": "New Storefront Access Token"
      },
      "userErrors": []
    }
  }
  ```

* ### storefrontAccessTokenCreate reference
