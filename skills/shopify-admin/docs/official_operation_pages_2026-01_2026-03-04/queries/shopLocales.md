---
title: shopLocales - GraphQL Admin
description: >-
  Returns the locales enabled on a shop. Each locale represents a language for
  translations and determines how content displays to customers in different
  markets.


  Use the optional `published` argument to filter for only the locales that are
  visible to customers. The response includes the ISO locale code, whether it's
  the shop's primary locale, and which
  [`MarketWebPresence`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketWebPresence)
  objects use each locale.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/shopLocales'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/shopLocales.md'
---

# shop​Locales

query

Requires `read_locales` access scope or `read_markets_home` access scope.

Returns the locales enabled on a shop. Each locale represents a language for translations and determines how content displays to customers in different markets.

Use the optional `published` argument to filter for only the locales that are visible to customers. The response includes the ISO locale code, whether it's the shop's primary locale, and which [`MarketWebPresence`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketWebPresence) objects use each locale.

## Arguments

* published

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Return only published locales.

***

## Possible returns

* Shop​Locale

  [\[Shop​Locale!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopLocale)

  A locale that's been enabled on a shop.

  * locale

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The locale ISO code.

  * market​Web​Presences

    [\[Market​Web​Presence!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketWebPresence)

    non-null

    The market web presences that use the locale.

  * name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The human-readable locale name.

  * primary

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the locale is the default locale for the shop.

  * published

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the locale is visible to buyers.

***

## Examples

* ### Retrieve a shop's locales

  #### Description

  The following query retrieves a list of the shop's enabled locales, including the locale tag, the published state, and whether the locale tag is the primary tag.

  #### Query

  ```graphql
  query {
    shopLocales {
      locale
      primary
      published
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
  "query": "query { shopLocales { locale primary published } }"
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
      shopLocales {
        locale
        primary
        published
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
      shopLocales {
        locale
        primary
        published
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
      shopLocales {
        locale
        primary
        published
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    shopLocales {
      locale
      primary
      published
    }
  }'
  ```

  #### Response

  ```json
  {
    "shopLocales": [
      {
        "locale": "en",
        "primary": true,
        "published": true
      },
      {
        "locale": "es",
        "primary": false,
        "published": true
      },
      {
        "locale": "fr",
        "primary": false,
        "published": true
      },
      {
        "locale": "ja",
        "primary": false,
        "published": true
      }
    ]
  }
  ```
