---
title: translatableResource - GraphQL Admin
description: >-
  Retrieves a resource that has translatable fields. Returns the resource's
  [`Translation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Translation)
  objects for different locales and markets, along with the original
  [`TranslatableContent`](https://shopify.dev/docs/api/admin-graphql/latest/objects/TranslatableContent)
  and digest values needed to register new translations. Provides access to
  existing translations, translatable content with digest hashes for translation
  registration, and nested translatable resources like
  [`ProductVariant`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant)
  objects or
  [`Metafield`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Metafield)
  objects.


  Learn more about [managing translated
  content](https://shopify.dev/docs/apps/build/markets/manage-translated-content).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/translatableResource
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/translatableResource.md
---

# translatable​Resource

query

Requires `read_translations` access scope.

Retrieves a resource that has translatable fields. Returns the resource's [`Translation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Translation) objects for different locales and markets, along with the original [`TranslatableContent`](https://shopify.dev/docs/api/admin-graphql/latest/objects/TranslatableContent) and digest values needed to register new translations. Provides access to existing translations, translatable content with digest hashes for translation registration, and nested translatable resources like [`ProductVariant`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant) objects or [`Metafield`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Metafield) objects.

Learn more about [managing translated content](https://shopify.dev/docs/apps/build/markets/manage-translated-content).

## Arguments

* resource​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  Find a translatable resource by ID.

***

## Possible returns

* Translatable​Resource

  [Translatable​Resource](https://shopify.dev/docs/api/admin-graphql/latest/objects/TranslatableResource)

  A resource in Shopify that contains fields available for translation into different languages. Accesses the resource's translatable content, existing [`Translation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Translation) objects, and any nested resources that can also be translated.

  The [`TranslatableContent`](https://shopify.dev/docs/api/admin-graphql/latest/objects/TranslatableContent) includes field keys, values, and digest hashes needed when [registering translations](https://shopify.dev/docs/api/admin-graphql/latest/mutations/translationsRegister).

  You can retrieve translations for specific [`Locale`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Locale) and [`Market`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Market) configurations. Each translation includes an `outdated` flag indicating whether the original content has changed since that translation was last updated.

  Learn more about [managing translated content](https://shopify.dev/docs/apps/build/markets/manage-translated-content).

  * nested​Translatable​Resources

    [Translatable​Resource​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/TranslatableResourceConnection)

    non-null

    Nested translatable resources under the current resource.

    * resource​Type

      [Translatable​Resource​Type](https://shopify.dev/docs/api/admin-graphql/latest/enums/TranslatableResourceType)

      ### Arguments

      Return only resources of a type.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * last

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * before

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * reverse

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Reverse the order of the underlying list.

    ***

  * resource​Id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    GID of the resource.

  * translatable​Content

    [\[Translatable​Content!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/TranslatableContent)

    non-null

    Translatable content.

    * market​Id

      [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      ### Arguments

      Filters translatable content by market ID. Use this argument to retrieve translatable content specific to a market.

    ***

  * translations

    [\[Translation!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Translation)

    non-null

    Translatable content translations (includes unpublished locales).

    * locale

      [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      required

      ### Arguments

      Filters translations by locale.

    * outdated

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Filters by outdated translations.

    * market​Id

      [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      Filters translations by market ID. Use this argument to retrieve content specific to a market.

    ***

***

## Examples

* ### Retrieve existing French translations on a collection

  #### Description

  Query the \`translations\` field on the return field to check existing translations associated with a collection.

  #### Query

  ```graphql
  query {
    translatableResource(resourceId: "gid://shopify/Collection/1007901140") {
      resourceId
      translations(locale: "fr") {
        key
        value
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
  "query": "query { translatableResource(resourceId: \"gid://shopify/Collection/1007901140\") { resourceId translations(locale: \"fr\") { key value } } }"
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
      translatableResource(resourceId: "gid://shopify/Collection/1007901140") {
        resourceId
        translations(locale: "fr") {
          key
          value
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
      translatableResource(resourceId: "gid://shopify/Collection/1007901140") {
        resourceId
        translations(locale: "fr") {
          key
          value
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
      translatableResource(resourceId: "gid://shopify/Collection/1007901140") {
        resourceId
        translations(locale: "fr") {
          key
          value
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
    translatableResource(resourceId: "gid://shopify/Collection/1007901140") {
      resourceId
      translations(locale: "fr") {
        key
        value
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "translatableResource": {
      "resourceId": "gid://shopify/Collection/1007901140",
      "translations": [
        {
          "key": "title",
          "value": "la collection"
        }
      ]
    }
  }
  ```

* ### Retrieve existing French translations specific to a market on a collection

  #### Description

  Make use of the optional \`marketId\` argument when querying the \`translations\` field to retrieve content specific to a market.

  #### Query

  ```graphql
  query {
    translatableResource(resourceId: "gid://shopify/Collection/1007901140") {
      resourceId
      translations(locale: "fr", marketId: "gid://shopify/Market/128989799") {
        key
        value
        market {
          id
          name
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
  "query": "query { translatableResource(resourceId: \"gid://shopify/Collection/1007901140\") { resourceId translations(locale: \"fr\", marketId: \"gid://shopify/Market/128989799\") { key value market { id name } } } }"
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
      translatableResource(resourceId: "gid://shopify/Collection/1007901140") {
        resourceId
        translations(locale: "fr", marketId: "gid://shopify/Market/128989799") {
          key
          value
          market {
            id
            name
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
      translatableResource(resourceId: "gid://shopify/Collection/1007901140") {
        resourceId
        translations(locale: "fr", marketId: "gid://shopify/Market/128989799") {
          key
          value
          market {
            id
            name
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
      translatableResource(resourceId: "gid://shopify/Collection/1007901140") {
        resourceId
        translations(locale: "fr", marketId: "gid://shopify/Market/128989799") {
          key
          value
          market {
            id
            name
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
    translatableResource(resourceId: "gid://shopify/Collection/1007901140") {
      resourceId
      translations(locale: "fr", marketId: "gid://shopify/Market/128989799") {
        key
        value
        market {
          id
          name
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "translatableResource": {
      "resourceId": "gid://shopify/Collection/1007901140",
      "translations": [
        {
          "key": "title",
          "value": "la collection canadienne",
          "market": {
            "id": "gid://shopify/Market/128989799",
            "name": "Canada"
          }
        }
      ]
    }
  }
  ```

* ### Retrieve translatable content for a collection

  #### Description

  Use this query as part of preparing to register translations. The \`digest\` value is required as an input argument when registering a translation.

  #### Query

  ```graphql
  query {
    translatableResource(resourceId: "gid://shopify/Collection/1007901140") {
      resourceId
      translatableContent {
        key
        value
        digest
        locale
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
  "query": "query { translatableResource(resourceId: \"gid://shopify/Collection/1007901140\") { resourceId translatableContent { key value digest locale } } }"
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
      translatableResource(resourceId: "gid://shopify/Collection/1007901140") {
        resourceId
        translatableContent {
          key
          value
          digest
          locale
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
      translatableResource(resourceId: "gid://shopify/Collection/1007901140") {
        resourceId
        translatableContent {
          key
          value
          digest
          locale
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
      translatableResource(resourceId: "gid://shopify/Collection/1007901140") {
        resourceId
        translatableContent {
          key
          value
          digest
          locale
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
    translatableResource(resourceId: "gid://shopify/Collection/1007901140") {
      resourceId
      translatableContent {
        key
        value
        digest
        locale
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "translatableResource": {
      "resourceId": "gid://shopify/Collection/1007901140",
      "translatableContent": [
        {
          "key": "title",
          "value": "Featured items",
          "digest": "a18b34037fda5b1afd720d4b85b86a8a75b5e389452f84f5b6d2b8e210869fd7",
          "locale": "en"
        },
        {
          "key": "body_html",
          "value": "Collection description",
          "digest": "e3fbf5a945f94e5ddbb6bef20f5e5e3a923b34bdf1eb170f770a8aa0fd163bfa",
          "locale": "en"
        },
        {
          "key": "handle",
          "value": "featured",
          "digest": "d562318e9c2d7e6d9c70de511fbf5d3081fae3d6699eed31c3a87c5a0bc6ca51",
          "locale": "en"
        }
      ]
    }
  }
  ```
