---
title: metafieldDefinitionUpdate - GraphQL Admin
description: >-
  Updates a
  [`MetafieldDefinition`](/docs/api/admin-graphql/2026-01/objects/MetafieldDefinition)'s
  configuration and settings. You can modify the definition's name, description,
  validation rules, access settings, capabilities, and constraints.


  The mutation updates access settings that control visibility across different
  APIs, such as the [GraphQL Admin
  API](https://shopify.dev/docs/api/admin-graphql), [Storefront
  API](https://shopify.dev/docs/api/storefront), and [Customer Account
  API](https://shopify.dev/docs/api/customer). It also enables capabilities like
  admin filtering or unique value validation, and modifies constraints that
  determine which resource subtypes the definition applies to.


  > Note: The type, namespace, key, and owner type identify the definition and
  so can't be changed.


  Learn more about [updating metafield
  definitions](https://shopify.dev/docs/apps/build/custom-data/metafields/definitions).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/metafieldDefinitionUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/metafieldDefinitionUpdate.md
---

# metafield​Definition​Update

mutation

Requires API client to have access to the namespace and the resource type associated with the metafield definition.

Updates a [`MetafieldDefinition`](https://shopify.dev/docs/api/admin-graphql/2026-01/objects/MetafieldDefinition)'s configuration and settings. You can modify the definition's name, description, validation rules, access settings, capabilities, and constraints.

The mutation updates access settings that control visibility across different APIs, such as the [GraphQL Admin API](https://shopify.dev/docs/api/admin-graphql), [Storefront API](https://shopify.dev/docs/api/storefront), and [Customer Account API](https://shopify.dev/docs/api/customer). It also enables capabilities like admin filtering or unique value validation, and modifies constraints that determine which resource subtypes the definition applies to.

***

**Note:** The type, namespace, key, and owner type identify the definition and so can\&#39;t be changed.

***

Learn more about [updating metafield definitions](https://shopify.dev/docs/apps/build/custom-data/metafields/definitions).

## Arguments

* definition

  [Metafield​Definition​Update​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MetafieldDefinitionUpdateInput)

  required

  The input fields for the metafield definition update.

***

## Metafield​Definition​Update​Payload returns

* updated​Definition

  [Metafield​Definition](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetafieldDefinition)

  The metafield definition that was updated.

* user​Errors

  [\[Metafield​Definition​Update​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetafieldDefinitionUpdateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

* validation​Job

  [Job](https://shopify.dev/docs/api/admin-graphql/latest/objects/Job)

  The asynchronous job updating the metafield definition's validation\_status.

***

## Examples

* ### Update a metafield definition

  #### Description

  To update a metafield definition, use the \`metafieldDefinitionUpdate\` mutation. The following example shows how to change a metafield definition's name from \`Pizza size\` to \`Pizza size (inches)\`.

  #### Query

  ```graphql
  mutation UpdateMetafieldDefinition($definition: MetafieldDefinitionUpdateInput!) {
    metafieldDefinitionUpdate(definition: $definition) {
      updatedDefinition {
        id
        name
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
    "definition": {
      "name": "Pizza size (inches)",
      "namespace": "bakery",
      "key": "pizza_size",
      "ownerType": "PRODUCT"
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
  "query": "mutation UpdateMetafieldDefinition($definition: MetafieldDefinitionUpdateInput!) { metafieldDefinitionUpdate(definition: $definition) { updatedDefinition { id name } userErrors { field message code } } }",
   "variables": {
      "definition": {
        "name": "Pizza size (inches)",
        "namespace": "bakery",
        "key": "pizza_size",
        "ownerType": "PRODUCT"
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
    mutation UpdateMetafieldDefinition($definition: MetafieldDefinitionUpdateInput!) {
      metafieldDefinitionUpdate(definition: $definition) {
        updatedDefinition {
          id
          name
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
          "definition": {
              "name": "Pizza size (inches)",
              "namespace": "bakery",
              "key": "pizza_size",
              "ownerType": "PRODUCT"
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
    mutation UpdateMetafieldDefinition($definition: MetafieldDefinitionUpdateInput!) {
      metafieldDefinitionUpdate(definition: $definition) {
        updatedDefinition {
          id
          name
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
    "definition": {
      "name": "Pizza size (inches)",
      "namespace": "bakery",
      "key": "pizza_size",
      "ownerType": "PRODUCT"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation UpdateMetafieldDefinition($definition: MetafieldDefinitionUpdateInput!) {
        metafieldDefinitionUpdate(definition: $definition) {
          updatedDefinition {
            id
            name
          }
          userErrors {
            field
            message
            code
          }
        }
      }`,
      "variables": {
          "definition": {
              "name": "Pizza size (inches)",
              "namespace": "bakery",
              "key": "pizza_size",
              "ownerType": "PRODUCT"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation UpdateMetafieldDefinition($definition: MetafieldDefinitionUpdateInput!) {
    metafieldDefinitionUpdate(definition: $definition) {
      updatedDefinition {
        id
        name
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
    "definition": {
      "name": "Pizza size (inches)",
      "namespace": "bakery",
      "key": "pizza_size",
      "ownerType": "PRODUCT"
    }
  }'
  ```

  #### Response

  ```json
  {
    "metafieldDefinitionUpdate": {
      "updatedDefinition": {
        "id": "gid://shopify/MetafieldDefinition/1071456170",
        "name": "Pizza size (inches)"
      },
      "userErrors": []
    }
  }
  ```

* ### Update a metafield definition with access controls

  #### Description

  To change the access settings on an existing definition, use the \`access\` property in your \`metafieldDefinitionUpdate\` mutation. You can set the default admin access setting and also specify additional grants to create, update or delete.

  #### Query

  ```graphql
  mutation UpdateMetafieldDefinition($definition: MetafieldDefinitionUpdateInput!) {
    metafieldDefinitionUpdate(definition: $definition) {
      updatedDefinition {
        id
        name
        access {
          admin
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
    "definition": {
      "name": "Pizza size (inches)",
      "namespace": "$app:bakery",
      "key": "pizza_size",
      "ownerType": "PRODUCT",
      "access": {
        "admin": "PRIVATE"
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
  "query": "mutation UpdateMetafieldDefinition($definition: MetafieldDefinitionUpdateInput!) { metafieldDefinitionUpdate(definition: $definition) { updatedDefinition { id name access { admin } } userErrors { field message code } } }",
   "variables": {
      "definition": {
        "name": "Pizza size (inches)",
        "namespace": "$app:bakery",
        "key": "pizza_size",
        "ownerType": "PRODUCT",
        "access": {
          "admin": "PRIVATE"
        }
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
    mutation UpdateMetafieldDefinition($definition: MetafieldDefinitionUpdateInput!) {
      metafieldDefinitionUpdate(definition: $definition) {
        updatedDefinition {
          id
          name
          access {
            admin
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
          "definition": {
              "name": "Pizza size (inches)",
              "namespace": "$app:bakery",
              "key": "pizza_size",
              "ownerType": "PRODUCT",
              "access": {
                  "admin": "PRIVATE"
              }
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
    mutation UpdateMetafieldDefinition($definition: MetafieldDefinitionUpdateInput!) {
      metafieldDefinitionUpdate(definition: $definition) {
        updatedDefinition {
          id
          name
          access {
            admin
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
    "definition": {
      "name": "Pizza size (inches)",
      "namespace": "$app:bakery",
      "key": "pizza_size",
      "ownerType": "PRODUCT",
      "access": {
        "admin": "PRIVATE"
      }
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation UpdateMetafieldDefinition($definition: MetafieldDefinitionUpdateInput!) {
        metafieldDefinitionUpdate(definition: $definition) {
          updatedDefinition {
            id
            name
            access {
              admin
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
          "definition": {
              "name": "Pizza size (inches)",
              "namespace": "$app:bakery",
              "key": "pizza_size",
              "ownerType": "PRODUCT",
              "access": {
                  "admin": "PRIVATE"
              }
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation UpdateMetafieldDefinition($definition: MetafieldDefinitionUpdateInput!) {
    metafieldDefinitionUpdate(definition: $definition) {
      updatedDefinition {
        id
        name
        access {
          admin
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
    "definition": {
      "name": "Pizza size (inches)",
      "namespace": "$app:bakery",
      "key": "pizza_size",
      "ownerType": "PRODUCT",
      "access": {
        "admin": "PRIVATE"
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "metafieldDefinitionUpdate": {
      "updatedDefinition": {
        "id": "gid://shopify/MetafieldDefinition/1071456171",
        "name": "Pizza size (inches)",
        "access": {
          "admin": "PRIVATE"
        }
      },
      "userErrors": []
    }
  }
  ```

* ### metafieldDefinitionUpdate reference
