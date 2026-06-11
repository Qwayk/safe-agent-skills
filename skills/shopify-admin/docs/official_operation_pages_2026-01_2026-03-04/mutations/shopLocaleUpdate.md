---
title: shopLocaleUpdate - GraphQL Admin
description: Updates a locale for a shop.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/shopLocaleUpdate'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/shopLocaleUpdate.md
---

# shop​Locale​Update

mutation

Requires `write_locales` access scope.

Updates a locale for a shop.

## Arguments

* locale

  [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  ISO code of the locale to update.

* shop​Locale

  [Shop​Locale​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ShopLocaleInput)

  required

  Specifies the input fields for a shop locale.

***

## Shop​Locale​Update​Payload returns

* shop​Locale

  [Shop​Locale](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopLocale)

  The locale that was updated.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Publish a locale

  #### Description

  Publishing a locale makes it available for translation. Make sure that you enable the locale before publishing it. A shop can have up to 20 alternate published locales.

  #### Query

  ```graphql
  mutation updateLocale($locale: String!, $shopLocale: ShopLocaleInput!) {
    shopLocaleUpdate(locale: $locale, shopLocale: $shopLocale) {
      userErrors {
        message
        field
      }
      shopLocale {
        name
        locale
        primary
        published
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "locale": "ko",
    "shopLocale": {
      "published": true
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
  "query": "mutation updateLocale($locale: String!, $shopLocale: ShopLocaleInput!) { shopLocaleUpdate(locale: $locale, shopLocale: $shopLocale) { userErrors { message field } shopLocale { name locale primary published } } }",
   "variables": {
      "locale": "ko",
      "shopLocale": {
        "published": true
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
    mutation updateLocale($locale: String!, $shopLocale: ShopLocaleInput!) {
      shopLocaleUpdate(locale: $locale, shopLocale: $shopLocale) {
        userErrors {
          message
          field
        }
        shopLocale {
          name
          locale
          primary
          published
        }
      }
    }`,
    {
      variables: {
          "locale": "ko",
          "shopLocale": {
              "published": true
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
    mutation updateLocale($locale: String!, $shopLocale: ShopLocaleInput!) {
      shopLocaleUpdate(locale: $locale, shopLocale: $shopLocale) {
        userErrors {
          message
          field
        }
        shopLocale {
          name
          locale
          primary
          published
        }
      }
    }
  QUERY

  variables = {
    "locale": "ko",
    "shopLocale": {
      "published": true
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation updateLocale($locale: String!, $shopLocale: ShopLocaleInput!) {
        shopLocaleUpdate(locale: $locale, shopLocale: $shopLocale) {
          userErrors {
            message
            field
          }
          shopLocale {
            name
            locale
            primary
            published
          }
        }
      }`,
      "variables": {
          "locale": "ko",
          "shopLocale": {
              "published": true
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation updateLocale($locale: String!, $shopLocale: ShopLocaleInput!) {
    shopLocaleUpdate(locale: $locale, shopLocale: $shopLocale) {
      userErrors {
        message
        field
      }
      shopLocale {
        name
        locale
        primary
        published
      }
    }
  }' \
  --variables \
  '{
    "locale": "ko",
    "shopLocale": {
      "published": true
    }
  }'
  ```

  #### Response

  ```json
  {
    "shopLocaleUpdate": {
      "userErrors": [],
      "shopLocale": {
        "name": "Korean",
        "locale": "ko",
        "primary": false,
        "published": true
      }
    }
  }
  ```

* ### Unpublish a locale

  #### Query

  ```graphql
  mutation updateLocale($locale: String!, $shopLocale: ShopLocaleInput!) {
    shopLocaleUpdate(locale: $locale, shopLocale: $shopLocale) {
      userErrors {
        message
        field
      }
      shopLocale {
        name
        locale
        primary
        published
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "locale": "ko",
    "shopLocale": {
      "published": false
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
  "query": "mutation updateLocale($locale: String!, $shopLocale: ShopLocaleInput!) { shopLocaleUpdate(locale: $locale, shopLocale: $shopLocale) { userErrors { message field } shopLocale { name locale primary published } } }",
   "variables": {
      "locale": "ko",
      "shopLocale": {
        "published": false
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
    mutation updateLocale($locale: String!, $shopLocale: ShopLocaleInput!) {
      shopLocaleUpdate(locale: $locale, shopLocale: $shopLocale) {
        userErrors {
          message
          field
        }
        shopLocale {
          name
          locale
          primary
          published
        }
      }
    }`,
    {
      variables: {
          "locale": "ko",
          "shopLocale": {
              "published": false
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
    mutation updateLocale($locale: String!, $shopLocale: ShopLocaleInput!) {
      shopLocaleUpdate(locale: $locale, shopLocale: $shopLocale) {
        userErrors {
          message
          field
        }
        shopLocale {
          name
          locale
          primary
          published
        }
      }
    }
  QUERY

  variables = {
    "locale": "ko",
    "shopLocale": {
      "published": false
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation updateLocale($locale: String!, $shopLocale: ShopLocaleInput!) {
        shopLocaleUpdate(locale: $locale, shopLocale: $shopLocale) {
          userErrors {
            message
            field
          }
          shopLocale {
            name
            locale
            primary
            published
          }
        }
      }`,
      "variables": {
          "locale": "ko",
          "shopLocale": {
              "published": false
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation updateLocale($locale: String!, $shopLocale: ShopLocaleInput!) {
    shopLocaleUpdate(locale: $locale, shopLocale: $shopLocale) {
      userErrors {
        message
        field
      }
      shopLocale {
        name
        locale
        primary
        published
      }
    }
  }' \
  --variables \
  '{
    "locale": "ko",
    "shopLocale": {
      "published": false
    }
  }'
  ```

  #### Response

  ```json
  {
    "shopLocaleUpdate": {
      "userErrors": [],
      "shopLocale": {
        "name": "Korean",
        "locale": "ko",
        "primary": false,
        "published": false
      }
    }
  }
  ```

* ### shopLocaleUpdate reference
