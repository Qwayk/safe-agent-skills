---
title: metafieldDefinitionDelete - GraphQL Admin
description: >-
  Deletes a
  [`MetafieldDefinition`](/docs/api/admin-graphql/2026-01/objects/MetafieldDefinition).
  You can identify the definition by providing either its owner type, namespace,
  and key, or its global ID.


  When you set
  [`deleteAllAssociatedMetafields`](/docs/api/admin-graphql/2026-01/mutations/metafieldDefinitionDelete#arguments-deleteAllAssociatedMetafields)
  to `true`, the mutation asynchronously deletes all
  [`Metafield`](/docs/api/admin-graphql/2026-01/objects/Metafield) objects that
  use this definition. This option must be `true` when deleting definitions
  under the `$app` namespace.


  Learn more about [deleting metafield
  definitions](https://shopify.dev/docs/apps/build/custom-data/metafields/definitions).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/metafieldDefinitionDelete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/metafieldDefinitionDelete.md
---

# metafield​Definition​Delete

mutation

Requires API client to have access to the resource type associated with the metafield definition.

Deletes a [`MetafieldDefinition`](https://shopify.dev/docs/api/admin-graphql/2026-01/objects/MetafieldDefinition). You can identify the definition by providing either its owner type, namespace, and key, or its global ID.

When you set [`deleteAllAssociatedMetafields`](https://shopify.dev/docs/api/admin-graphql/2026-01/mutations/metafieldDefinitionDelete#arguments-deleteAllAssociatedMetafields) to `true`, the mutation asynchronously deletes all [`Metafield`](https://shopify.dev/docs/api/admin-graphql/2026-01/objects/Metafield) objects that use this definition. This option must be `true` when deleting definitions under the `$app` namespace.

Learn more about [deleting metafield definitions](https://shopify.dev/docs/apps/build/custom-data/metafields/definitions).

## Arguments

* delete​All​Associated​Metafields

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Whether to delete all associated metafields.

* id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The id of the metafield definition to delete. Using `identifier` is preferred.

* identifier

  [Metafield​Definition​Identifier​Input](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MetafieldDefinitionIdentifierInput)

  The identifier of the metafield definition to delete.

***

## Metafield​Definition​Delete​Payload returns

* deleted​Definition

  [Metafield​Definition​Identifier](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetafieldDefinitionIdentifier)

  The metafield definition that was deleted.

* deleted​Definition​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the deleted metafield definition.

* user​Errors

  [\[Metafield​Definition​Delete​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetafieldDefinitionDeleteUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Delete a metafield definition

  #### Description

  To delete a metafield definition, use the \`metafieldDefinitionDelete\` mutation. The following example shows how to delete the metafield definition for \`bakery.ingredients\`, and also deletes all metafields that use the definition.

  #### Query

  ```graphql
  mutation DeleteMetafieldDefinition($id: ID!, $deleteAllAssociatedMetafields: Boolean!) {
    metafieldDefinitionDelete(id: $id, deleteAllAssociatedMetafields: $deleteAllAssociatedMetafields) {
      deletedDefinitionId
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
    "id": "gid://shopify/MetafieldDefinition/1071456130",
    "deleteAllAssociatedMetafields": true
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation DeleteMetafieldDefinition($id: ID!, $deleteAllAssociatedMetafields: Boolean!) { metafieldDefinitionDelete(id: $id, deleteAllAssociatedMetafields: $deleteAllAssociatedMetafields) { deletedDefinitionId userErrors { field message code } } }",
   "variables": {
      "id": "gid://shopify/MetafieldDefinition/1071456130",
      "deleteAllAssociatedMetafields": true
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
    mutation DeleteMetafieldDefinition($id: ID!, $deleteAllAssociatedMetafields: Boolean!) {
      metafieldDefinitionDelete(id: $id, deleteAllAssociatedMetafields: $deleteAllAssociatedMetafields) {
        deletedDefinitionId
        userErrors {
          field
          message
          code
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/MetafieldDefinition/1071456130",
          "deleteAllAssociatedMetafields": true
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
    mutation DeleteMetafieldDefinition($id: ID!, $deleteAllAssociatedMetafields: Boolean!) {
      metafieldDefinitionDelete(id: $id, deleteAllAssociatedMetafields: $deleteAllAssociatedMetafields) {
        deletedDefinitionId
        userErrors {
          field
          message
          code
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/MetafieldDefinition/1071456130",
    "deleteAllAssociatedMetafields": true
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation DeleteMetafieldDefinition($id: ID!, $deleteAllAssociatedMetafields: Boolean!) {
        metafieldDefinitionDelete(id: $id, deleteAllAssociatedMetafields: $deleteAllAssociatedMetafields) {
          deletedDefinitionId
          userErrors {
            field
            message
            code
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/MetafieldDefinition/1071456130",
          "deleteAllAssociatedMetafields": true
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation DeleteMetafieldDefinition($id: ID!, $deleteAllAssociatedMetafields: Boolean!) {
    metafieldDefinitionDelete(id: $id, deleteAllAssociatedMetafields: $deleteAllAssociatedMetafields) {
      deletedDefinitionId
      userErrors {
        field
        message
        code
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/MetafieldDefinition/1071456130",
    "deleteAllAssociatedMetafields": true
  }'
  ```

  #### Response

  ```json
  {
    "metafieldDefinitionDelete": {
      "deletedDefinitionId": "gid://shopify/MetafieldDefinition/1071456130",
      "userErrors": []
    }
  }
  ```

* ### metafieldDefinitionDelete reference
