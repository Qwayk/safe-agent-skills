---
title: metafieldDefinitionUnpin - GraphQL Admin
description: >-
  You can organize your metafields in your Shopify admin by pinning/unpinning
  metafield definitions.

  The order of your pinned metafield definitions determines the order in which
  your metafields are displayed

  on the corresponding pages in your Shopify admin. By default, only pinned
  metafields are automatically displayed.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/metafieldDefinitionUnpin
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/metafieldDefinitionUnpin.md
---

# metafield​Definition​Unpin

mutation

Requires API client to have access to the namespace and the resource type associated with the metafield definition.

You can organize your metafields in your Shopify admin by pinning/unpinning metafield definitions. The order of your pinned metafield definitions determines the order in which your metafields are displayed on the corresponding pages in your Shopify admin. By default, only pinned metafields are automatically displayed.

## Arguments

* definition​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the metafield definition to unpin. Using `identifier` is preferred.

* identifier

  [Metafield​Definition​Identifier​Input](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MetafieldDefinitionIdentifierInput)

  The identifier of the metafield definition to unpin.

***

## Metafield​Definition​Unpin​Payload returns

* unpinned​Definition

  [Metafield​Definition](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetafieldDefinition)

  The metafield definition that was unpinned.

* user​Errors

  [\[Metafield​Definition​Unpin​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetafieldDefinitionUnpinUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Unpin a metafield definition

  #### Description

  Unpins a metafield definition so it isn't automatically displayed in the Shopify admin.

  #### Query

  ```graphql
  mutation metafieldDefinitionUnpin($definitionId: ID!) {
    metafieldDefinitionUnpin(definitionId: $definitionId) {
      unpinnedDefinition {
        name
        key
        namespace
        pinnedPosition
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
    "definitionId": "gid://shopify/MetafieldDefinition/1071456133"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation metafieldDefinitionUnpin($definitionId: ID!) { metafieldDefinitionUnpin(definitionId: $definitionId) { unpinnedDefinition { name key namespace pinnedPosition } userErrors { field message } } }",
   "variables": {
      "definitionId": "gid://shopify/MetafieldDefinition/1071456133"
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
    mutation metafieldDefinitionUnpin($definitionId: ID!) {
      metafieldDefinitionUnpin(definitionId: $definitionId) {
        unpinnedDefinition {
          name
          key
          namespace
          pinnedPosition
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "definitionId": "gid://shopify/MetafieldDefinition/1071456133"
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
    mutation metafieldDefinitionUnpin($definitionId: ID!) {
      metafieldDefinitionUnpin(definitionId: $definitionId) {
        unpinnedDefinition {
          name
          key
          namespace
          pinnedPosition
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "definitionId": "gid://shopify/MetafieldDefinition/1071456133"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation metafieldDefinitionUnpin($definitionId: ID!) {
        metafieldDefinitionUnpin(definitionId: $definitionId) {
          unpinnedDefinition {
            name
            key
            namespace
            pinnedPosition
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "definitionId": "gid://shopify/MetafieldDefinition/1071456133"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation metafieldDefinitionUnpin($definitionId: ID!) {
    metafieldDefinitionUnpin(definitionId: $definitionId) {
      unpinnedDefinition {
        name
        key
        namespace
        pinnedPosition
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "definitionId": "gid://shopify/MetafieldDefinition/1071456133"
  }'
  ```

  #### Response

  ```json
  {
    "metafieldDefinitionUnpin": {
      "unpinnedDefinition": {
        "name": "Instructions to wash your product",
        "key": "wash",
        "namespace": "instructions",
        "pinnedPosition": null
      },
      "userErrors": []
    }
  }
  ```

* ### metafieldDefinitionUnpin reference
