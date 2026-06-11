---
title: metaobjectUpsert - GraphQL Admin
description: >-
  Creates or updates a
  [`Metaobject`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Metaobject)
  based on its handle. If a metaobject with the specified handle exists, the
  mutation updates it with the provided field values. If no matching metaobject
  exists, the mutation creates a new one.


  The handle serves as a unique identifier within a metaobject type. Field
  values map to the
  [`MetaobjectDefinition`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectDefinition)'s
  field keys and overwrite existing values during updates.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/metaobjectUpsert'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/metaobjectUpsert.md
---

# metaobject​Upsert

mutation

Requires `write_metaobjects` access scope.

Creates or updates a [`Metaobject`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Metaobject) based on its handle. If a metaobject with the specified handle exists, the mutation updates it with the provided field values. If no matching metaobject exists, the mutation creates a new one.

The handle serves as a unique identifier within a metaobject type. Field values map to the [`MetaobjectDefinition`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectDefinition)'s field keys and overwrite existing values during updates.

## Arguments

* handle

  [Metaobject​Handle​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MetaobjectHandleInput)

  required

  The identifier of the metaobject to upsert.

* metaobject

  [Metaobject​Upsert​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MetaobjectUpsertInput)

  required

  The parameters to upsert the metaobject.

***

## Metaobject​Upsert​Payload returns

* metaobject

  [Metaobject](https://shopify.dev/docs/api/admin-graphql/latest/objects/Metaobject)

  The created or updated metaobject.

* user​Errors

  [\[Metaobject​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Upsert a metaobject

  #### Description

  To upsert a metaobject, you can use the \`metaobjectUpsert\` mutation with the \`handle\` and \`metaobject\` input arguments which will either create a new metaobject or update an existing one. The following example uses upsert to create a new "color" metaobject with the handle "indigo-swatch" since it does not already exist.

  #### Query

  ```graphql
  mutation UpsertMetaobject($handle: MetaobjectHandleInput!, $metaobject: MetaobjectUpsertInput!) {
    metaobjectUpsert(handle: $handle, metaobject: $metaobject) {
      metaobject {
        handle
        hex: field(key: "hex") {
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
    "handle": {
      "type": "color",
      "handle": "indigo-swatch"
    },
    "metaobject": {
      "fields": [
        {
          "key": "hex",
          "value": "#4B0082"
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
  "query": "mutation UpsertMetaobject($handle: MetaobjectHandleInput!, $metaobject: MetaobjectUpsertInput!) { metaobjectUpsert(handle: $handle, metaobject: $metaobject) { metaobject { handle hex: field(key: \"hex\") { value } } userErrors { field message code } } }",
   "variables": {
      "handle": {
        "type": "color",
        "handle": "indigo-swatch"
      },
      "metaobject": {
        "fields": [
          {
            "key": "hex",
            "value": "#4B0082"
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
    mutation UpsertMetaobject($handle: MetaobjectHandleInput!, $metaobject: MetaobjectUpsertInput!) {
      metaobjectUpsert(handle: $handle, metaobject: $metaobject) {
        metaobject {
          handle
          hex: field(key: "hex") {
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
          "handle": {
              "type": "color",
              "handle": "indigo-swatch"
          },
          "metaobject": {
              "fields": [
                  {
                      "key": "hex",
                      "value": "#4B0082"
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
    mutation UpsertMetaobject($handle: MetaobjectHandleInput!, $metaobject: MetaobjectUpsertInput!) {
      metaobjectUpsert(handle: $handle, metaobject: $metaobject) {
        metaobject {
          handle
          hex: field(key: "hex") {
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
    "handle": {
      "type": "color",
      "handle": "indigo-swatch"
    },
    "metaobject": {
      "fields": [
        {
          "key": "hex",
          "value": "#4B0082"
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
      "query": `mutation UpsertMetaobject($handle: MetaobjectHandleInput!, $metaobject: MetaobjectUpsertInput!) {
        metaobjectUpsert(handle: $handle, metaobject: $metaobject) {
          metaobject {
            handle
            hex: field(key: "hex") {
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
          "handle": {
              "type": "color",
              "handle": "indigo-swatch"
          },
          "metaobject": {
              "fields": [
                  {
                      "key": "hex",
                      "value": "#4B0082"
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
  'mutation UpsertMetaobject($handle: MetaobjectHandleInput!, $metaobject: MetaobjectUpsertInput!) {
    metaobjectUpsert(handle: $handle, metaobject: $metaobject) {
      metaobject {
        handle
        hex: field(key: "hex") {
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
    "handle": {
      "type": "color",
      "handle": "indigo-swatch"
    },
    "metaobject": {
      "fields": [
        {
          "key": "hex",
          "value": "#4B0082"
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "metaobjectUpsert": {
      "metaobject": {
        "handle": "indigo-swatch",
        "hex": {
          "value": "#4B0082"
        }
      },
      "userErrors": []
    }
  }
  ```

* ### metaobjectUpsert reference
