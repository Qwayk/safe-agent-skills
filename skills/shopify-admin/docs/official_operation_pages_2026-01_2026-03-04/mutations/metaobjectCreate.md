---
title: metaobjectCreate - GraphQL Admin
description: >-
  Creates a metaobject entry based on an existing
  [`MetaobjectDefinition`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectDefinition).
  The type must match a definition that already exists in the shop.


  Specify field values using key-value pairs that correspond to the field
  definitions. The mutation generates a unique handle automatically if you don't
  provide one. You can also configure capabilities like publishable status to
  control the metaobject's visibility across channels.


  Learn more about [managing
  metaobjects](https://shopify.dev/docs/apps/build/custom-data/metaobjects/manage-metaobjects).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/metaobjectCreate'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/metaobjectCreate.md
---

# metaobject​Create

mutation

Requires `write_metaobjects` access scope.

Creates a metaobject entry based on an existing [`MetaobjectDefinition`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectDefinition). The type must match a definition that already exists in the shop.

Specify field values using key-value pairs that correspond to the field definitions. The mutation generates a unique handle automatically if you don't provide one. You can also configure capabilities like publishable status to control the metaobject's visibility across channels.

Learn more about [managing metaobjects](https://shopify.dev/docs/apps/build/custom-data/metaobjects/manage-metaobjects).

## Arguments

* metaobject

  [Metaobject​Create​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MetaobjectCreateInput)

  required

  The parameters for the metaobject to create.

***

## Metaobject​Create​Payload returns

* metaobject

  [Metaobject](https://shopify.dev/docs/api/admin-graphql/latest/objects/Metaobject)

  The created metaobject.

* user​Errors

  [\[Metaobject​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a metaobject

  #### Description

  To create a metaobject, you can use the \`metaobjectCreate\` mutation along with the metaobject as an argument providing the type and fields you want to create. A \`MetaobjectDefinition\` with the specified type and fields must already exist. The following example creates a new "Lookbook" metaobject with the \`winter-2023\` handle and the season field set to \`winter\`.

  #### Query

  ```graphql
  mutation CreateMetaobject($metaobject: MetaobjectCreateInput!) {
    metaobjectCreate(metaobject: $metaobject) {
      metaobject {
        handle
        season: field(key: "season") {
          value
        }
      }
      userErrors {
        field
        message
        code
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "metaobject": {
      "type": "lookbook",
      "handle": "winter-2023",
      "fields": [
        {
          "key": "season",
          "value": "winter"
        }
      ]
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
  "query": "mutation CreateMetaobject($metaobject: MetaobjectCreateInput!) { metaobjectCreate(metaobject: $metaobject) { metaobject { handle season: field(key: \"season\") { value } } userErrors { field message code } } }",
   "variables": {
      "metaobject": {
        "type": "lookbook",
        "handle": "winter-2023",
        "fields": [
          {
            "key": "season",
            "value": "winter"
          }
        ]
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
    mutation CreateMetaobject($metaobject: MetaobjectCreateInput!) {
      metaobjectCreate(metaobject: $metaobject) {
        metaobject {
          handle
          season: field(key: "season") {
            value
          }
        }
        userErrors {
          field
          message
          code
        }
      }
    }`,
    {
      variables: {
          "metaobject": {
              "type": "lookbook",
              "handle": "winter-2023",
              "fields": [
                  {
                      "key": "season",
                      "value": "winter"
                  }
              ]
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
    mutation CreateMetaobject($metaobject: MetaobjectCreateInput!) {
      metaobjectCreate(metaobject: $metaobject) {
        metaobject {
          handle
          season: field(key: "season") {
            value
          }
        }
        userErrors {
          field
          message
          code
        }
      }
    }
  QUERY

  variables = {
    "metaobject": {
      "type": "lookbook",
      "handle": "winter-2023",
      "fields": [
        {
          "key": "season",
          "value": "winter"
        }
      ]
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation CreateMetaobject($metaobject: MetaobjectCreateInput!) {
        metaobjectCreate(metaobject: $metaobject) {
          metaobject {
            handle
            season: field(key: "season") {
              value
            }
          }
          userErrors {
            field
            message
            code
          }
        }
      }`,
      "variables": {
          "metaobject": {
              "type": "lookbook",
              "handle": "winter-2023",
              "fields": [
                  {
                      "key": "season",
                      "value": "winter"
                  }
              ]
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation CreateMetaobject($metaobject: MetaobjectCreateInput!) {
    metaobjectCreate(metaobject: $metaobject) {
      metaobject {
        handle
        season: field(key: "season") {
          value
        }
      }
      userErrors {
        field
        message
        code
      }
    }
  }' \
  --variables \
  '{
    "metaobject": {
      "type": "lookbook",
      "handle": "winter-2023",
      "fields": [
        {
          "key": "season",
          "value": "winter"
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "metaobjectCreate": {
      "metaobject": {
        "handle": "winter-2023",
        "season": {
          "value": "winter"
        }
      },
      "userErrors": []
    }
  }
  ```

* ### metaobjectCreate reference
