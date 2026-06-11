---
title: translationsRegister - GraphQL Admin
description: >-
  Creates or updates translations for a resource's [translatable
  content](https://shopify.dev/docs/api/admin-graphql/latest/objects/TranslatableContent).


  Each translation requires a digest value from the resource's translatable
  content. Use the
  [`translatableResource`](https://shopify.dev/docs/api/admin-graphql/latest/queries/translatableResource)
  query to get a resource's translatable content and digest values before
  creating translations. You can optionally scope translations to specific
  markets using the `marketId` field in each translation input.


  Learn more about [managing
  translations](https://shopify.dev/docs/apps/build/markets/manage-translated-content).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/translationsRegister
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/translationsRegister.md
---

# translations​Register

mutation

Requires `write_translations` access scope.

Creates or updates translations for a resource's [translatable content](https://shopify.dev/docs/api/admin-graphql/latest/objects/TranslatableContent).

Each translation requires a digest value from the resource's translatable content. Use the [`translatableResource`](https://shopify.dev/docs/api/admin-graphql/latest/queries/translatableResource) query to get a resource's translatable content and digest values before creating translations. You can optionally scope translations to specific markets using the `marketId` field in each translation input.

Learn more about [managing translations](https://shopify.dev/docs/apps/build/markets/manage-translated-content).

## Arguments

* resource​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  ID of the resource that is being translated.

* translations

  [\[Translation​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/TranslationInput)

  required

  Specifies the input fields for a translation.

***

## Translations​Register​Payload returns

* translations

  [\[Translation!\]](https://shopify.dev/docs/api/admin-graphql/latest/objects/Translation)

  The translations that were created or updated.

* user​Errors

  [\[Translation​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/TranslationUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Register a French product title

  #### Description

  A successfully registered translation will be immediately visible to buyers if the locale is already published. In this example, the registered content will be visible to all buyers browsing in French from any market, unless there exists a market-specific translation for that market. To retrieve the \`translatableContentDigest\`, call the \`translatableResource\` query beforehand.

  #### Query

  ```graphql
  mutation translationsRegister($resourceId: ID!, $translations: [TranslationInput!]!) {
    translationsRegister(resourceId: $resourceId, translations: $translations) {
      userErrors {
        message
        field
      }
      translations {
        key
        value
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "resourceId": "gid://shopify/Product/20995642",
    "translations": [
      {
        "locale": "fr",
        "key": "title",
        "value": "L'élément",
        "translatableContentDigest": "4e5b548d6d61f0006840aca106f7464a4b59e5a854317d5b57861b8423901bf6"
      }
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
  "query": "mutation translationsRegister($resourceId: ID!, $translations: [TranslationInput!]!) { translationsRegister(resourceId: $resourceId, translations: $translations) { userErrors { message field } translations { key value } } }",
   "variables": {
      "resourceId": "gid://shopify/Product/20995642",
      "translations": [
        {
          "locale": "fr",
          "key": "title",
          "value": "L'\''élément",
          "translatableContentDigest": "4e5b548d6d61f0006840aca106f7464a4b59e5a854317d5b57861b8423901bf6"
        }
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
    mutation translationsRegister($resourceId: ID!, $translations: [TranslationInput!]!) {
      translationsRegister(resourceId: $resourceId, translations: $translations) {
        userErrors {
          message
          field
        }
        translations {
          key
          value
        }
      }
    }`,
    {
      variables: {
          "resourceId": "gid://shopify/Product/20995642",
          "translations": [
              {
                  "locale": "fr",
                  "key": "title",
                  "value": "L'élément",
                  "translatableContentDigest": "4e5b548d6d61f0006840aca106f7464a4b59e5a854317d5b57861b8423901bf6"
              }
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
    mutation translationsRegister($resourceId: ID!, $translations: [TranslationInput!]!) {
      translationsRegister(resourceId: $resourceId, translations: $translations) {
        userErrors {
          message
          field
        }
        translations {
          key
          value
        }
      }
    }
  QUERY

  variables = {
    "resourceId": "gid://shopify/Product/20995642",
    "translations": [
      {
        "locale": "fr",
        "key": "title",
        "value": "L'élément",
        "translatableContentDigest": "4e5b548d6d61f0006840aca106f7464a4b59e5a854317d5b57861b8423901bf6"
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation translationsRegister($resourceId: ID!, $translations: [TranslationInput!]!) {
        translationsRegister(resourceId: $resourceId, translations: $translations) {
          userErrors {
            message
            field
          }
          translations {
            key
            value
          }
        }
      }`,
      "variables": {
          "resourceId": "gid://shopify/Product/20995642",
          "translations": [
              {
                  "locale": "fr",
                  "key": "title",
                  "value": "L'élément",
                  "translatableContentDigest": "4e5b548d6d61f0006840aca106f7464a4b59e5a854317d5b57861b8423901bf6"
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation translationsRegister($resourceId: ID!, $translations: [TranslationInput!]!) {
    translationsRegister(resourceId: $resourceId, translations: $translations) {
      userErrors {
        message
        field
      }
      translations {
        key
        value
      }
    }
  }' \
  --variables \
  '{
    "resourceId": "gid://shopify/Product/20995642",
    "translations": [
      {
        "locale": "fr",
        "key": "title",
        "value": "L'élément",
        "translatableContentDigest": "4e5b548d6d61f0006840aca106f7464a4b59e5a854317d5b57861b8423901bf6"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "translationsRegister": {
      "userErrors": [],
      "translations": [
        {
          "key": "title",
          "value": "L'élément"
        }
      ]
    }
  }
  ```

* ### Register a French product title specific to a market

  #### Description

  To register content that surfaces only to buyers in a specific market, make use of the \`TranslationInput\` object's optional \`marketId\` field. In this example, the words "L'élément canadien" will only be visible to buyers in the specified market, which has an ID of \`gid://shopify/Market/128989799\`.

  #### Query

  ```graphql
  mutation translationsRegister($resourceId: ID!, $translations: [TranslationInput!]!) {
    translationsRegister(resourceId: $resourceId, translations: $translations) {
      userErrors {
        message
        field
      }
      translations {
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

  #### Variables

  ```json
  {
    "resourceId": "gid://shopify/Product/20995642",
    "translations": [
      {
        "locale": "fr",
        "key": "title",
        "value": "L'élément canadien",
        "translatableContentDigest": "4e5b548d6d61f0006840aca106f7464a4b59e5a854317d5b57861b8423901bf6",
        "marketId": "gid://shopify/Market/128989799"
      }
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
  "query": "mutation translationsRegister($resourceId: ID!, $translations: [TranslationInput!]!) { translationsRegister(resourceId: $resourceId, translations: $translations) { userErrors { message field } translations { key value market { id name } } } }",
   "variables": {
      "resourceId": "gid://shopify/Product/20995642",
      "translations": [
        {
          "locale": "fr",
          "key": "title",
          "value": "L'\''élément canadien",
          "translatableContentDigest": "4e5b548d6d61f0006840aca106f7464a4b59e5a854317d5b57861b8423901bf6",
          "marketId": "gid://shopify/Market/128989799"
        }
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
    mutation translationsRegister($resourceId: ID!, $translations: [TranslationInput!]!) {
      translationsRegister(resourceId: $resourceId, translations: $translations) {
        userErrors {
          message
          field
        }
        translations {
          key
          value
          market {
            id
            name
          }
        }
      }
    }`,
    {
      variables: {
          "resourceId": "gid://shopify/Product/20995642",
          "translations": [
              {
                  "locale": "fr",
                  "key": "title",
                  "value": "L'élément canadien",
                  "translatableContentDigest": "4e5b548d6d61f0006840aca106f7464a4b59e5a854317d5b57861b8423901bf6",
                  "marketId": "gid://shopify/Market/128989799"
              }
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
    mutation translationsRegister($resourceId: ID!, $translations: [TranslationInput!]!) {
      translationsRegister(resourceId: $resourceId, translations: $translations) {
        userErrors {
          message
          field
        }
        translations {
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

  variables = {
    "resourceId": "gid://shopify/Product/20995642",
    "translations": [
      {
        "locale": "fr",
        "key": "title",
        "value": "L'élément canadien",
        "translatableContentDigest": "4e5b548d6d61f0006840aca106f7464a4b59e5a854317d5b57861b8423901bf6",
        "marketId": "gid://shopify/Market/128989799"
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation translationsRegister($resourceId: ID!, $translations: [TranslationInput!]!) {
        translationsRegister(resourceId: $resourceId, translations: $translations) {
          userErrors {
            message
            field
          }
          translations {
            key
            value
            market {
              id
              name
            }
          }
        }
      }`,
      "variables": {
          "resourceId": "gid://shopify/Product/20995642",
          "translations": [
              {
                  "locale": "fr",
                  "key": "title",
                  "value": "L'élément canadien",
                  "translatableContentDigest": "4e5b548d6d61f0006840aca106f7464a4b59e5a854317d5b57861b8423901bf6",
                  "marketId": "gid://shopify/Market/128989799"
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation translationsRegister($resourceId: ID!, $translations: [TranslationInput!]!) {
    translationsRegister(resourceId: $resourceId, translations: $translations) {
      userErrors {
        message
        field
      }
      translations {
        key
        value
        market {
          id
          name
        }
      }
    }
  }' \
  --variables \
  '{
    "resourceId": "gid://shopify/Product/20995642",
    "translations": [
      {
        "locale": "fr",
        "key": "title",
        "value": "L'élément canadien",
        "translatableContentDigest": "4e5b548d6d61f0006840aca106f7464a4b59e5a854317d5b57861b8423901bf6",
        "marketId": "gid://shopify/Market/128989799"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "translationsRegister": {
      "userErrors": [],
      "translations": [
        {
          "key": "title",
          "value": "L'élément canadien",
          "market": {
            "id": "gid://shopify/Market/128989799",
            "name": "Canada"
          }
        }
      ]
    }
  }
  ```

* ### Register a product title in the shop default language specific to a market

  #### Description

  To register content in the shop default language that surfaces only to buyers in a specific market, make use of the \`TranslationInput\` object's optional \`marketId\` field. In this example, the shop default language is English, and the words "Canadian element" will only be visible to buyers in the specified market, which has an ID of \`gid://shopify/Market/128989799\`.

  #### Query

  ```graphql
  mutation translationsRegister($resourceId: ID!, $translations: [TranslationInput!]!) {
    translationsRegister(resourceId: $resourceId, translations: $translations) {
      userErrors {
        message
        field
      }
      translations {
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

  #### Variables

  ```json
  {
    "resourceId": "gid://shopify/Product/20995642",
    "translations": [
      {
        "locale": "en",
        "key": "title",
        "value": "Canadian element",
        "translatableContentDigest": "4e5b548d6d61f0006840aca106f7464a4b59e5a854317d5b57861b8423901bf6",
        "marketId": "gid://shopify/Market/128989799"
      }
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
  "query": "mutation translationsRegister($resourceId: ID!, $translations: [TranslationInput!]!) { translationsRegister(resourceId: $resourceId, translations: $translations) { userErrors { message field } translations { key value market { id name } } } }",
   "variables": {
      "resourceId": "gid://shopify/Product/20995642",
      "translations": [
        {
          "locale": "en",
          "key": "title",
          "value": "Canadian element",
          "translatableContentDigest": "4e5b548d6d61f0006840aca106f7464a4b59e5a854317d5b57861b8423901bf6",
          "marketId": "gid://shopify/Market/128989799"
        }
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
    mutation translationsRegister($resourceId: ID!, $translations: [TranslationInput!]!) {
      translationsRegister(resourceId: $resourceId, translations: $translations) {
        userErrors {
          message
          field
        }
        translations {
          key
          value
          market {
            id
            name
          }
        }
      }
    }`,
    {
      variables: {
          "resourceId": "gid://shopify/Product/20995642",
          "translations": [
              {
                  "locale": "en",
                  "key": "title",
                  "value": "Canadian element",
                  "translatableContentDigest": "4e5b548d6d61f0006840aca106f7464a4b59e5a854317d5b57861b8423901bf6",
                  "marketId": "gid://shopify/Market/128989799"
              }
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
    mutation translationsRegister($resourceId: ID!, $translations: [TranslationInput!]!) {
      translationsRegister(resourceId: $resourceId, translations: $translations) {
        userErrors {
          message
          field
        }
        translations {
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

  variables = {
    "resourceId": "gid://shopify/Product/20995642",
    "translations": [
      {
        "locale": "en",
        "key": "title",
        "value": "Canadian element",
        "translatableContentDigest": "4e5b548d6d61f0006840aca106f7464a4b59e5a854317d5b57861b8423901bf6",
        "marketId": "gid://shopify/Market/128989799"
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation translationsRegister($resourceId: ID!, $translations: [TranslationInput!]!) {
        translationsRegister(resourceId: $resourceId, translations: $translations) {
          userErrors {
            message
            field
          }
          translations {
            key
            value
            market {
              id
              name
            }
          }
        }
      }`,
      "variables": {
          "resourceId": "gid://shopify/Product/20995642",
          "translations": [
              {
                  "locale": "en",
                  "key": "title",
                  "value": "Canadian element",
                  "translatableContentDigest": "4e5b548d6d61f0006840aca106f7464a4b59e5a854317d5b57861b8423901bf6",
                  "marketId": "gid://shopify/Market/128989799"
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation translationsRegister($resourceId: ID!, $translations: [TranslationInput!]!) {
    translationsRegister(resourceId: $resourceId, translations: $translations) {
      userErrors {
        message
        field
      }
      translations {
        key
        value
        market {
          id
          name
        }
      }
    }
  }' \
  --variables \
  '{
    "resourceId": "gid://shopify/Product/20995642",
    "translations": [
      {
        "locale": "en",
        "key": "title",
        "value": "Canadian element",
        "translatableContentDigest": "4e5b548d6d61f0006840aca106f7464a4b59e5a854317d5b57861b8423901bf6",
        "marketId": "gid://shopify/Market/128989799"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "translationsRegister": {
      "userErrors": [],
      "translations": [
        {
          "key": "title",
          "value": "Canadian element",
          "market": {
            "id": "gid://shopify/Market/128989799",
            "name": "Canada"
          }
        }
      ]
    }
  }
  ```

* ### translationsRegister reference
