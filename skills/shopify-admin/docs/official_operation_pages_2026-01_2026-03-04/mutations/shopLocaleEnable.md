---
title: shopLocaleEnable - GraphQL Admin
description: Adds a locale for a shop. The newly added locale is in the unpublished state.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/shopLocaleEnable'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/shopLocaleEnable.md
---

# shop​Locale​Enable

mutation

Requires `write_locales` access scope.

Adds a locale for a shop. The newly added locale is in the unpublished state.

## Arguments

* locale

  [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  ISO code of the locale to enable.

* market​Web​Presence​Ids

  [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The list of markets web presences to add the locale to.

***

## Shop​Locale​Enable​Payload returns

* shop​Locale

  [Shop​Locale](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopLocale)

  ISO code of the locale that was enabled.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Enable a locale

  #### Description

  A locale must be enabled before it can be published. The shopLocaleEnable mutation takes a locale tag. The shop locale is requested in the response to verify that the localewas enabled correctly. A shop can have up to 20 enabled locales.

  #### Query

  ```graphql
  mutation enableLocale($locale: String!) {
    shopLocaleEnable(locale: $locale) {
      userErrors {
        message
        field
      }
      shopLocale {
        locale
        name
        primary
        published
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "locale": "ko"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation enableLocale($locale: String!) { shopLocaleEnable(locale: $locale) { userErrors { message field } shopLocale { locale name primary published } } }",
   "variables": {
      "locale": "ko"
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
    mutation enableLocale($locale: String!) {
      shopLocaleEnable(locale: $locale) {
        userErrors {
          message
          field
        }
        shopLocale {
          locale
          name
          primary
          published
        }
      }
    }`,
    {
      variables: {
          "locale": "ko"
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
    mutation enableLocale($locale: String!) {
      shopLocaleEnable(locale: $locale) {
        userErrors {
          message
          field
        }
        shopLocale {
          locale
          name
          primary
          published
        }
      }
    }
  QUERY

  variables = {
    "locale": "ko"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation enableLocale($locale: String!) {
        shopLocaleEnable(locale: $locale) {
          userErrors {
            message
            field
          }
          shopLocale {
            locale
            name
            primary
            published
          }
        }
      }`,
      "variables": {
          "locale": "ko"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation enableLocale($locale: String!) {
    shopLocaleEnable(locale: $locale) {
      userErrors {
        message
        field
      }
      shopLocale {
        locale
        name
        primary
        published
      }
    }
  }' \
  --variables \
  '{
    "locale": "ko"
  }'
  ```

  #### Response

  ```json
  {
    "shopLocaleEnable": {
      "userErrors": [],
      "shopLocale": {
        "locale": "ko",
        "name": "Korean",
        "primary": false,
        "published": false
      }
    }
  }
  ```

* ### shopLocaleEnable reference
