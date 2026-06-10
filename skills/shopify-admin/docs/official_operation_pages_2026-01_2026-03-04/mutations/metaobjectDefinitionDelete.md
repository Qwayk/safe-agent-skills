---
title: metaobjectDefinitionDelete - GraphQL Admin
description: >-
  Deletes the specified metaobject definition.

  Also deletes all related metafield definitions, metaobjects, and metafields
  asynchronously.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/metaobjectDefinitionDelete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/metaobjectDefinitionDelete.md
---

# metaobject​Definition​Delete

mutation

Requires `write_metaobject_definitions` access scope.

Deletes the specified metaobject definition. Also deletes all related metafield definitions, metaobjects, and metafields asynchronously.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the metaobjects definition to delete.

***

## Metaobject​Definition​Delete​Payload returns

* deleted​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the deleted metaobjects definition.

* user​Errors

  [\[Metaobject​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Delete a metaobject definition

  #### Description

  To delete a metaobject definition, use the \`metaobjectDefinitionDelete\` mutation. The following example shows how to delete the metaobject definition for "Lookbook". Be careful: Deleting a metaobject definition will cascade and delete all of its metaobjects.

  #### Query

  ```graphql
  mutation DeleteMetaobjectDefinition($id: ID!) {
    metaobjectDefinitionDelete(id: $id) {
      deletedId
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
    "id": "gid://shopify/MetaobjectDefinition/578408816"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation DeleteMetaobjectDefinition($id: ID!) { metaobjectDefinitionDelete(id: $id) { deletedId userErrors { field message code } } }",
   "variables": {
      "id": "gid://shopify/MetaobjectDefinition/578408816"
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
    mutation DeleteMetaobjectDefinition($id: ID!) {
      metaobjectDefinitionDelete(id: $id) {
        deletedId
        userErrors {
          field
          message
          code
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/MetaobjectDefinition/578408816"
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
    mutation DeleteMetaobjectDefinition($id: ID!) {
      metaobjectDefinitionDelete(id: $id) {
        deletedId
        userErrors {
          field
          message
          code
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/MetaobjectDefinition/578408816"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation DeleteMetaobjectDefinition($id: ID!) {
        metaobjectDefinitionDelete(id: $id) {
          deletedId
          userErrors {
            field
            message
            code
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/MetaobjectDefinition/578408816"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation DeleteMetaobjectDefinition($id: ID!) {
    metaobjectDefinitionDelete(id: $id) {
      deletedId
      userErrors {
        field
        message
        code
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/MetaobjectDefinition/578408816"
  }'
  ```

  #### Response

  ```json
  {
    "metaobjectDefinitionDelete": {
      "deletedId": "gid://shopify/MetaobjectDefinition/578408816",
      "userErrors": []
    }
  }
  ```

* ### metaobjectDefinitionDelete reference
