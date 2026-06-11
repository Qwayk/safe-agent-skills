---
title: translationsRemove - GraphQL Admin
description: Deletes translations.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/translationsRemove
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/translationsRemove.md
---

# translations​Remove

mutation

Requires `write_translations` access scope.

Deletes translations.

## Arguments

* locales

  [\[String!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  The list of translation locales. Only locales returned in `shopLocales` are valid.

* market​Ids

  [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The list of market IDs.

* resource​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  ID of the translatable resource for which translations are being deleted.

* translation​Keys

  [\[String!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  The list of translation keys.

***

## Translations​Remove​Payload returns

* translations

  [\[Translation!\]](https://shopify.dev/docs/api/admin-graphql/latest/objects/Translation)

  The translations that were deleted.

* user​Errors

  [\[Translation​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/TranslationUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Remove a French product title translation

  #### Description

  Translations matching all of the inputs will be removed. In this example, we are removing the product title's French translation that is not specific to any market.

  #### Query

  ```graphql
  mutation translationsRemove($resourceId: ID!, $translationKeys: [String!]!, $locales: [String!]!) {
    translationsRemove(resourceId: $resourceId, translationKeys: $translationKeys, locales: $locales) {
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
    "locales": [
      "fr"
    ],
    "translationKeys": [
      "title"
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
  "query": "mutation translationsRemove($resourceId: ID!, $translationKeys: [String!]!, $locales: [String!]!) { translationsRemove(resourceId: $resourceId, translationKeys: $translationKeys, locales: $locales) { userErrors { message field } translations { key value } } }",
   "variables": {
      "resourceId": "gid://shopify/Product/20995642",
      "locales": [
        "fr"
      ],
      "translationKeys": [
        "title"
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
    mutation translationsRemove($resourceId: ID!, $translationKeys: [String!]!, $locales: [String!]!) {
      translationsRemove(resourceId: $resourceId, translationKeys: $translationKeys, locales: $locales) {
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
          "locales": [
              "fr"
          ],
          "translationKeys": [
              "title"
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
    mutation translationsRemove($resourceId: ID!, $translationKeys: [String!]!, $locales: [String!]!) {
      translationsRemove(resourceId: $resourceId, translationKeys: $translationKeys, locales: $locales) {
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
    "locales": [
      "fr"
    ],
    "translationKeys": [
      "title"
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation translationsRemove($resourceId: ID!, $translationKeys: [String!]!, $locales: [String!]!) {
        translationsRemove(resourceId: $resourceId, translationKeys: $translationKeys, locales: $locales) {
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
          "locales": [
              "fr"
          ],
          "translationKeys": [
              "title"
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation translationsRemove($resourceId: ID!, $translationKeys: [String!]!, $locales: [String!]!) {
    translationsRemove(resourceId: $resourceId, translationKeys: $translationKeys, locales: $locales) {
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
    "locales": [
      "fr"
    ],
    "translationKeys": [
      "title"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "translationsRemove": {
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

* ### Remove a French product title translation specific to a market

  #### Description

  To remove content that surfaces only to buyers in specific markets, make use of the optional \`marketIds\` argument. In this example, the targeted market has an ID of \`gid://shopify/Market/128989799\`.

  #### Query

  ```graphql
  mutation translationsRemove($resourceId: ID!, $translationKeys: [String!]!, $locales: [String!]!, $marketIds: [ID!]) {
    translationsRemove(resourceId: $resourceId, translationKeys: $translationKeys, locales: $locales, marketIds: $marketIds) {
      userErrors {
        message
        field
      }
      translations {
        key
        value
        market {
          id
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "resourceId": "gid://shopify/Product/20995642",
    "locales": [
      "fr"
    ],
    "translationKeys": [
      "title"
    ],
    "marketIds": [
      "gid://shopify/Market/128989799"
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
  "query": "mutation translationsRemove($resourceId: ID!, $translationKeys: [String!]!, $locales: [String!]!, $marketIds: [ID!]) { translationsRemove(resourceId: $resourceId, translationKeys: $translationKeys, locales: $locales, marketIds: $marketIds) { userErrors { message field } translations { key value market { id } } } }",
   "variables": {
      "resourceId": "gid://shopify/Product/20995642",
      "locales": [
        "fr"
      ],
      "translationKeys": [
        "title"
      ],
      "marketIds": [
        "gid://shopify/Market/128989799"
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
    mutation translationsRemove($resourceId: ID!, $translationKeys: [String!]!, $locales: [String!]!, $marketIds: [ID!]) {
      translationsRemove(resourceId: $resourceId, translationKeys: $translationKeys, locales: $locales, marketIds: $marketIds) {
        userErrors {
          message
          field
        }
        translations {
          key
          value
          market {
            id
          }
        }
      }
    }`,
    {
      variables: {
          "resourceId": "gid://shopify/Product/20995642",
          "locales": [
              "fr"
          ],
          "translationKeys": [
              "title"
          ],
          "marketIds": [
              "gid://shopify/Market/128989799"
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
    mutation translationsRemove($resourceId: ID!, $translationKeys: [String!]!, $locales: [String!]!, $marketIds: [ID!]) {
      translationsRemove(resourceId: $resourceId, translationKeys: $translationKeys, locales: $locales, marketIds: $marketIds) {
        userErrors {
          message
          field
        }
        translations {
          key
          value
          market {
            id
          }
        }
      }
    }
  QUERY

  variables = {
    "resourceId": "gid://shopify/Product/20995642",
    "locales": [
      "fr"
    ],
    "translationKeys": [
      "title"
    ],
    "marketIds": [
      "gid://shopify/Market/128989799"
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation translationsRemove($resourceId: ID!, $translationKeys: [String!]!, $locales: [String!]!, $marketIds: [ID!]) {
        translationsRemove(resourceId: $resourceId, translationKeys: $translationKeys, locales: $locales, marketIds: $marketIds) {
          userErrors {
            message
            field
          }
          translations {
            key
            value
            market {
              id
            }
          }
        }
      }`,
      "variables": {
          "resourceId": "gid://shopify/Product/20995642",
          "locales": [
              "fr"
          ],
          "translationKeys": [
              "title"
          ],
          "marketIds": [
              "gid://shopify/Market/128989799"
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation translationsRemove($resourceId: ID!, $translationKeys: [String!]!, $locales: [String!]!, $marketIds: [ID!]) {
    translationsRemove(resourceId: $resourceId, translationKeys: $translationKeys, locales: $locales, marketIds: $marketIds) {
      userErrors {
        message
        field
      }
      translations {
        key
        value
        market {
          id
        }
      }
    }
  }' \
  --variables \
  '{
    "resourceId": "gid://shopify/Product/20995642",
    "locales": [
      "fr"
    ],
    "translationKeys": [
      "title"
    ],
    "marketIds": [
      "gid://shopify/Market/128989799"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "translationsRemove": {
      "userErrors": [],
      "translations": [
        {
          "key": "title",
          "value": "L'élément canadien",
          "market": {
            "id": "gid://shopify/Market/128989799"
          }
        }
      ]
    }
  }
  ```

* ### translationsRemove reference
