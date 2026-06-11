---
title: metafieldDefinitionCreate - GraphQL Admin
description: >-
  Creates a
  [`MetafieldDefinition`](/docs/api/admin-graphql/2026-01/objects/MetafieldDefinition)
  that establishes structure and validation rules for metafields. The definition
  specifies the data type, validation constraints, and access permissions for
  metafields with a given namespace and key combination.


  When you create a new definition, the system validates any existing
  unstructured metafields matching the same owner type, namespace, and key
  against it. The system updates each valid metafield's type to match the
  definition. Invalid metafields remain unchanged but must conform to the
  definition when updated.


  Learn more about [creating metafield
  definitions](https://shopify.dev/docs/apps/build/custom-data/metafields/definitions).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/metafieldDefinitionCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/metafieldDefinitionCreate.md
---

# metafield​Definition​Create

mutation

Requires API client to have access to the namespace and the resource type associated with the metafield definition.

Creates a [`MetafieldDefinition`](https://shopify.dev/docs/api/admin-graphql/2026-01/objects/MetafieldDefinition) that establishes structure and validation rules for metafields. The definition specifies the data type, validation constraints, and access permissions for metafields with a given namespace and key combination.

When you create a new definition, the system validates any existing unstructured metafields matching the same owner type, namespace, and key against it. The system updates each valid metafield's type to match the definition. Invalid metafields remain unchanged but must conform to the definition when updated.

Learn more about [creating metafield definitions](https://shopify.dev/docs/apps/build/custom-data/metafields/definitions).

## Arguments

* definition

  [Metafield​Definition​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MetafieldDefinitionInput)

  required

  Specifies the input fields for a metafield definition.

***

## Metafield​Definition​Create​Payload returns

* created​Definition

  [Metafield​Definition](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetafieldDefinition)

  The metafield definition that was created.

* user​Errors

  [\[Metafield​Definition​Create​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetafieldDefinitionCreateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a metafield definition

  #### Description

  You can create a metafield definition using the \`metafieldDefinitionCreate\` mutation. The following example shows how to add a metafield definition called "Ingredients" to the Product resource, which stores multi-line text (such as a list of ingredients used to make the product).

  #### Query

  ```graphql
  mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
    metafieldDefinitionCreate(definition: $definition) {
      createdDefinition {
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
      "name": "Ingredients",
      "namespace": "bakery",
      "key": "ingredients",
      "description": "A list of ingredients used to make the product.",
      "type": "multi_line_text_field",
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
  "query": "mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) { metafieldDefinitionCreate(definition: $definition) { createdDefinition { id name } userErrors { field message code } } }",
   "variables": {
      "definition": {
        "name": "Ingredients",
        "namespace": "bakery",
        "key": "ingredients",
        "description": "A list of ingredients used to make the product.",
        "type": "multi_line_text_field",
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
    mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
      metafieldDefinitionCreate(definition: $definition) {
        createdDefinition {
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
              "name": "Ingredients",
              "namespace": "bakery",
              "key": "ingredients",
              "description": "A list of ingredients used to make the product.",
              "type": "multi_line_text_field",
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
    mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
      metafieldDefinitionCreate(definition: $definition) {
        createdDefinition {
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
      "name": "Ingredients",
      "namespace": "bakery",
      "key": "ingredients",
      "description": "A list of ingredients used to make the product.",
      "type": "multi_line_text_field",
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
      "query": `mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
        metafieldDefinitionCreate(definition: $definition) {
          createdDefinition {
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
              "name": "Ingredients",
              "namespace": "bakery",
              "key": "ingredients",
              "description": "A list of ingredients used to make the product.",
              "type": "multi_line_text_field",
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
  'mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
    metafieldDefinitionCreate(definition: $definition) {
      createdDefinition {
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
      "name": "Ingredients",
      "namespace": "bakery",
      "key": "ingredients",
      "description": "A list of ingredients used to make the product.",
      "type": "multi_line_text_field",
      "ownerType": "PRODUCT"
    }
  }'
  ```

  #### Response

  ```json
  {
    "metafieldDefinitionCreate": {
      "createdDefinition": {
        "id": "gid://shopify/MetafieldDefinition/1071456166",
        "name": "Ingredients"
      },
      "userErrors": []
    }
  }
  ```

* ### Create a metafield definition to be used with automated collections

  #### Description

  You can use metafield definitions as collection condition rules for automated collections. The first step is to enable the metafield definition \`useAsCollectionCondition\` flag. This flag can be activated on a maximum of 128 definitions per product and variant metafield defintions. Note that you cannot delete the metafield definition if it is being used as a collection condition rule.

  #### Query

  ```graphql
  mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
    metafieldDefinitionCreate(definition: $definition) {
      createdDefinition {
        id
        name
        useAsCollectionCondition
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
      "name": "Material",
      "namespace": "custom",
      "key": "material",
      "description": "A list of materials used to make the product.",
      "type": "list.single_line_text_field",
      "ownerType": "PRODUCT",
      "useAsCollectionCondition": true
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
  "query": "mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) { metafieldDefinitionCreate(definition: $definition) { createdDefinition { id name useAsCollectionCondition } userErrors { field message code } } }",
   "variables": {
      "definition": {
        "name": "Material",
        "namespace": "custom",
        "key": "material",
        "description": "A list of materials used to make the product.",
        "type": "list.single_line_text_field",
        "ownerType": "PRODUCT",
        "useAsCollectionCondition": true
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
    mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
      metafieldDefinitionCreate(definition: $definition) {
        createdDefinition {
          id
          name
          useAsCollectionCondition
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
              "name": "Material",
              "namespace": "custom",
              "key": "material",
              "description": "A list of materials used to make the product.",
              "type": "list.single_line_text_field",
              "ownerType": "PRODUCT",
              "useAsCollectionCondition": true
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
    mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
      metafieldDefinitionCreate(definition: $definition) {
        createdDefinition {
          id
          name
          useAsCollectionCondition
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
      "name": "Material",
      "namespace": "custom",
      "key": "material",
      "description": "A list of materials used to make the product.",
      "type": "list.single_line_text_field",
      "ownerType": "PRODUCT",
      "useAsCollectionCondition": true
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
        metafieldDefinitionCreate(definition: $definition) {
          createdDefinition {
            id
            name
            useAsCollectionCondition
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
              "name": "Material",
              "namespace": "custom",
              "key": "material",
              "description": "A list of materials used to make the product.",
              "type": "list.single_line_text_field",
              "ownerType": "PRODUCT",
              "useAsCollectionCondition": true
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
    metafieldDefinitionCreate(definition: $definition) {
      createdDefinition {
        id
        name
        useAsCollectionCondition
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
      "name": "Material",
      "namespace": "custom",
      "key": "material",
      "description": "A list of materials used to make the product.",
      "type": "list.single_line_text_field",
      "ownerType": "PRODUCT",
      "useAsCollectionCondition": true
    }
  }'
  ```

  #### Response

  ```json
  {
    "metafieldDefinitionCreate": {
      "createdDefinition": {
        "id": "gid://shopify/MetafieldDefinition/1071456167",
        "name": "Material",
        "useAsCollectionCondition": true
      },
      "userErrors": []
    }
  }
  ```

* ### Create a metafield definition with access controls

  #### Description

  The following example shows how to create a metafield definition in a namespace with a reserved prefix that is read- only to the merchant, grants explicit access to 2 specified apps, and no other app can access it via the Admin API.

  #### Query

  ```graphql
  mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
    metafieldDefinitionCreate(definition: $definition) {
      createdDefinition {
        id
        namespace
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
      "name": "Pizza size",
      "namespace": "$app:bakery",
      "key": "pizza_size",
      "type": "dimension",
      "description": "The size (diameter) of the pizza in inches.",
      "ownerType": "PRODUCT",
      "access": {
        "admin": "MERCHANT_READ"
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
  "query": "mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) { metafieldDefinitionCreate(definition: $definition) { createdDefinition { id namespace access { admin } } userErrors { field message code } } }",
   "variables": {
      "definition": {
        "name": "Pizza size",
        "namespace": "$app:bakery",
        "key": "pizza_size",
        "type": "dimension",
        "description": "The size (diameter) of the pizza in inches.",
        "ownerType": "PRODUCT",
        "access": {
          "admin": "MERCHANT_READ"
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
    mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
      metafieldDefinitionCreate(definition: $definition) {
        createdDefinition {
          id
          namespace
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
              "name": "Pizza size",
              "namespace": "$app:bakery",
              "key": "pizza_size",
              "type": "dimension",
              "description": "The size (diameter) of the pizza in inches.",
              "ownerType": "PRODUCT",
              "access": {
                  "admin": "MERCHANT_READ"
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
    mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
      metafieldDefinitionCreate(definition: $definition) {
        createdDefinition {
          id
          namespace
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
      "name": "Pizza size",
      "namespace": "$app:bakery",
      "key": "pizza_size",
      "type": "dimension",
      "description": "The size (diameter) of the pizza in inches.",
      "ownerType": "PRODUCT",
      "access": {
        "admin": "MERCHANT_READ"
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
      "query": `mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
        metafieldDefinitionCreate(definition: $definition) {
          createdDefinition {
            id
            namespace
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
              "name": "Pizza size",
              "namespace": "$app:bakery",
              "key": "pizza_size",
              "type": "dimension",
              "description": "The size (diameter) of the pizza in inches.",
              "ownerType": "PRODUCT",
              "access": {
                  "admin": "MERCHANT_READ"
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
  'mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
    metafieldDefinitionCreate(definition: $definition) {
      createdDefinition {
        id
        namespace
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
      "name": "Pizza size",
      "namespace": "$app:bakery",
      "key": "pizza_size",
      "type": "dimension",
      "description": "The size (diameter) of the pizza in inches.",
      "ownerType": "PRODUCT",
      "access": {
        "admin": "MERCHANT_READ"
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "metafieldDefinitionCreate": {
      "createdDefinition": {
        "id": "gid://shopify/MetafieldDefinition/1071456164",
        "namespace": "app--23898054--bakery",
        "access": {
          "admin": "MERCHANT_READ"
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Create a metafield definition with validations

  #### Description

  The following example shows how to create a metafield definition called \`Pizza size\` with a \`minimum\` size of 9 and a \`maximum\` size of 15.

  #### Query

  ```graphql
  mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
    metafieldDefinitionCreate(definition: $definition) {
      createdDefinition {
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
      "name": "Pizza size",
      "namespace": "bakery",
      "key": "pizza_size",
      "type": "dimension",
      "description": "The size (diameter) of the pizza in inches.",
      "validations": [
        {
          "name": "min",
          "value": "{\"unit\": \"INCHES\", \"value\": \"9\"}"
        },
        {
          "name": "max",
          "value": "{\"unit\": \"INCHES\", \"value\": \"15\"}"
        }
      ],
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
  "query": "mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) { metafieldDefinitionCreate(definition: $definition) { createdDefinition { id name } userErrors { field message code } } }",
   "variables": {
      "definition": {
        "name": "Pizza size",
        "namespace": "bakery",
        "key": "pizza_size",
        "type": "dimension",
        "description": "The size (diameter) of the pizza in inches.",
        "validations": [
          {
            "name": "min",
            "value": "{\"unit\": \"INCHES\", \"value\": \"9\"}"
          },
          {
            "name": "max",
            "value": "{\"unit\": \"INCHES\", \"value\": \"15\"}"
          }
        ],
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
    mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
      metafieldDefinitionCreate(definition: $definition) {
        createdDefinition {
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
              "name": "Pizza size",
              "namespace": "bakery",
              "key": "pizza_size",
              "type": "dimension",
              "description": "The size (diameter) of the pizza in inches.",
              "validations": [
                  {
                      "name": "min",
                      "value": "{\"unit\": \"INCHES\", \"value\": \"9\"}"
                  },
                  {
                      "name": "max",
                      "value": "{\"unit\": \"INCHES\", \"value\": \"15\"}"
                  }
              ],
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
    mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
      metafieldDefinitionCreate(definition: $definition) {
        createdDefinition {
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
      "name": "Pizza size",
      "namespace": "bakery",
      "key": "pizza_size",
      "type": "dimension",
      "description": "The size (diameter) of the pizza in inches.",
      "validations": [
        {
          "name": "min",
          "value": "{\"unit\": \"INCHES\", \"value\": \"9\"}"
        },
        {
          "name": "max",
          "value": "{\"unit\": \"INCHES\", \"value\": \"15\"}"
        }
      ],
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
      "query": `mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
        metafieldDefinitionCreate(definition: $definition) {
          createdDefinition {
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
              "name": "Pizza size",
              "namespace": "bakery",
              "key": "pizza_size",
              "type": "dimension",
              "description": "The size (diameter) of the pizza in inches.",
              "validations": [
                  {
                      "name": "min",
                      "value": "{\"unit\": \"INCHES\", \"value\": \"9\"}"
                  },
                  {
                      "name": "max",
                      "value": "{\"unit\": \"INCHES\", \"value\": \"15\"}"
                  }
              ],
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
  'mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
    metafieldDefinitionCreate(definition: $definition) {
      createdDefinition {
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
      "name": "Pizza size",
      "namespace": "bakery",
      "key": "pizza_size",
      "type": "dimension",
      "description": "The size (diameter) of the pizza in inches.",
      "validations": [
        {
          "name": "min",
          "value": "{\"unit\": \"INCHES\", \"value\": \"9\"}"
        },
        {
          "name": "max",
          "value": "{\"unit\": \"INCHES\", \"value\": \"15\"}"
        }
      ],
      "ownerType": "PRODUCT"
    }
  }'
  ```

  #### Response

  ```json
  {
    "metafieldDefinitionCreate": {
      "createdDefinition": {
        "id": "gid://shopify/MetafieldDefinition/1071456165",
        "name": "Pizza size"
      },
      "userErrors": []
    }
  }
  ```

* ### metafieldDefinitionCreate reference
