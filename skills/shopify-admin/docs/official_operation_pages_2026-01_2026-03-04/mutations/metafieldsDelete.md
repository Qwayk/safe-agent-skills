---
title: metafieldsDelete - GraphQL Admin
description: >-
  Deletes [`Metafield`](/docs/api/admin-graphql/2026-01/objects/Metafield)
  objects in bulk by specifying combinations of owner ID, namespace, and key.


  Returns the identifiers of successfully deleted metafields. If a specified
  metafield doesn't exist, then the mutation still succeeds but returns `null`
  for that identifier in the response.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/metafieldsDelete'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/metafieldsDelete.md
---

# metafields​Delete

mutation

Requires access defined by each metafield input `ownerId` scalar's type in a `MetafieldsSetInput` field. For example, setting a metafield on a `PRODUCT` requires the same access as mutating a `PRODUCT`.

Deletes [`Metafield`](https://shopify.dev/docs/api/admin-graphql/2026-01/objects/Metafield) objects in bulk by specifying combinations of owner ID, namespace, and key.

Returns the identifiers of successfully deleted metafields. If a specified metafield doesn't exist, then the mutation still succeeds but returns `null` for that identifier in the response.

## Arguments

* metafields

  [\[Metafield​Identifier​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MetafieldIdentifierInput)

  required

  A list of identifiers specifying metafields to delete. At least one identifier must be specified.

***

## Metafields​Delete​Payload returns

* deleted​Metafields

  [\[Metafield​Identifier\]](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetafieldIdentifier)

  List of metafield identifiers that were deleted, null if the corresponding metafield isn't found.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Deletes a metafield by its ID

  #### Query

  ```graphql
  mutation MetafieldsDelete($metafields: [MetafieldIdentifierInput!]!) {
    metafieldsDelete(metafields: $metafields) {
      deletedMetafields {
        key
        namespace
        ownerId
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
    "metafields": [
      {
        "ownerId": "gid://shopify/Product/20995642",
        "namespace": "inventory",
        "key": "today"
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
  "query": "mutation MetafieldsDelete($metafields: [MetafieldIdentifierInput!]!) { metafieldsDelete(metafields: $metafields) { deletedMetafields { key namespace ownerId } userErrors { field message } } }",
   "variables": {
      "metafields": [
        {
          "ownerId": "gid://shopify/Product/20995642",
          "namespace": "inventory",
          "key": "today"
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
    mutation MetafieldsDelete($metafields: [MetafieldIdentifierInput!]!) {
      metafieldsDelete(metafields: $metafields) {
        deletedMetafields {
          key
          namespace
          ownerId
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "metafields": [
              {
                  "ownerId": "gid://shopify/Product/20995642",
                  "namespace": "inventory",
                  "key": "today"
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
    mutation MetafieldsDelete($metafields: [MetafieldIdentifierInput!]!) {
      metafieldsDelete(metafields: $metafields) {
        deletedMetafields {
          key
          namespace
          ownerId
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "metafields": [
      {
        "ownerId": "gid://shopify/Product/20995642",
        "namespace": "inventory",
        "key": "today"
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
      "query": `mutation MetafieldsDelete($metafields: [MetafieldIdentifierInput!]!) {
        metafieldsDelete(metafields: $metafields) {
          deletedMetafields {
            key
            namespace
            ownerId
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "metafields": [
              {
                  "ownerId": "gid://shopify/Product/20995642",
                  "namespace": "inventory",
                  "key": "today"
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
  'mutation MetafieldsDelete($metafields: [MetafieldIdentifierInput!]!) {
    metafieldsDelete(metafields: $metafields) {
      deletedMetafields {
        key
        namespace
        ownerId
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "metafields": [
      {
        "ownerId": "gid://shopify/Product/20995642",
        "namespace": "inventory",
        "key": "today"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "metafieldsDelete": {
      "deletedMetafields": [
        {
          "key": "today",
          "namespace": "inventory",
          "ownerId": "gid://shopify/Product/20995642"
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### metafieldsDelete reference
