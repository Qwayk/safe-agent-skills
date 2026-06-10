---
title: metaobjectDefinitionCreate - GraphQL Admin
description: >-
  Creates a metaobject definition that establishes the structure for custom data
  objects in your store. The definition specifies the fields, data types, and
  access permissions that all
  [`Metaobject`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Metaobject)
  entries of this type share.


  Use the `type` field to create a unique namespace for your metaobjects. Prefix
  the type with `$app:` to reserve the definition for your app's exclusive use.
  The definition can include capabilities like publishable status or translation
  eligibility, to extend how metaobjects integrate with Shopify's features.


  Learn more about [managing
  metaobjects](https://shopify.dev/docs/apps/build/custom-data/metaobjects/manage-metaobjects).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/metaobjectDefinitionCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/metaobjectDefinitionCreate.md
---

# metaobject​Definition​Create

mutation

Requires `write_metaobject_definitions` access scope.

Creates a metaobject definition that establishes the structure for custom data objects in your store. The definition specifies the fields, data types, and access permissions that all [`Metaobject`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Metaobject) entries of this type share.

Use the `type` field to create a unique namespace for your metaobjects. Prefix the type with `$app:` to reserve the definition for your app's exclusive use. The definition can include capabilities like publishable status or translation eligibility, to extend how metaobjects integrate with Shopify's features.

Learn more about [managing metaobjects](https://shopify.dev/docs/apps/build/custom-data/metaobjects/manage-metaobjects).

## Arguments

* definition

  [Metaobject​Definition​Create​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MetaobjectDefinitionCreateInput)

  required

  The input fields for creating a metaobject definition.

***

## Metaobject​Definition​Create​Payload returns

* metaobject​Definition

  [Metaobject​Definition](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectDefinition)

  The created metaobject definition.

* user​Errors

  [\[Metaobject​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a metaobject definition

  #### Description

  A metaobject definition provides the blueprint for a metaobject by defining its type and possible fields. You can create a metaobject definition using the \`metaobjectDefinitionCreate\` mutation. The following example shows how to add a metaobject definition called "Color swatch" that has a single line text field called "Hex" which stores the color's hex code.

  #### Query

  ```graphql
  mutation CreateMetaobjectDefinition($definition: MetaobjectDefinitionCreateInput!) {
    metaobjectDefinitionCreate(definition: $definition) {
      metaobjectDefinition {
        name
        type
        fieldDefinitions {
          name
          key
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
      "name": "Color swatch",
      "type": "color-swatch",
      "fieldDefinitions": [
        {
          "name": "Hex",
          "key": "hex",
          "type": "single_line_text_field",
          "validations": [
            {
              "name": "regex",
              "value": "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
            }
          ]
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
  "query": "mutation CreateMetaobjectDefinition($definition: MetaobjectDefinitionCreateInput!) { metaobjectDefinitionCreate(definition: $definition) { metaobjectDefinition { name type fieldDefinitions { name key } } userErrors { field message code } } }",
   "variables": {
      "definition": {
        "name": "Color swatch",
        "type": "color-swatch",
        "fieldDefinitions": [
          {
            "name": "Hex",
            "key": "hex",
            "type": "single_line_text_field",
            "validations": [
              {
                "name": "regex",
                "value": "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
              }
            ]
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
    mutation CreateMetaobjectDefinition($definition: MetaobjectDefinitionCreateInput!) {
      metaobjectDefinitionCreate(definition: $definition) {
        metaobjectDefinition {
          name
          type
          fieldDefinitions {
            name
            key
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
              "name": "Color swatch",
              "type": "color-swatch",
              "fieldDefinitions": [
                  {
                      "name": "Hex",
                      "key": "hex",
                      "type": "single_line_text_field",
                      "validations": [
                          {
                              "name": "regex",
                              "value": "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
                          }
                      ]
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
    mutation CreateMetaobjectDefinition($definition: MetaobjectDefinitionCreateInput!) {
      metaobjectDefinitionCreate(definition: $definition) {
        metaobjectDefinition {
          name
          type
          fieldDefinitions {
            name
            key
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
      "name": "Color swatch",
      "type": "color-swatch",
      "fieldDefinitions": [
        {
          "name": "Hex",
          "key": "hex",
          "type": "single_line_text_field",
          "validations": [
            {
              "name": "regex",
              "value": "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
            }
          ]
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
      "query": `mutation CreateMetaobjectDefinition($definition: MetaobjectDefinitionCreateInput!) {
        metaobjectDefinitionCreate(definition: $definition) {
          metaobjectDefinition {
            name
            type
            fieldDefinitions {
              name
              key
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
              "name": "Color swatch",
              "type": "color-swatch",
              "fieldDefinitions": [
                  {
                      "name": "Hex",
                      "key": "hex",
                      "type": "single_line_text_field",
                      "validations": [
                          {
                              "name": "regex",
                              "value": "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
                          }
                      ]
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
  'mutation CreateMetaobjectDefinition($definition: MetaobjectDefinitionCreateInput!) {
    metaobjectDefinitionCreate(definition: $definition) {
      metaobjectDefinition {
        name
        type
        fieldDefinitions {
          name
          key
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
      "name": "Color swatch",
      "type": "color-swatch",
      "fieldDefinitions": [
        {
          "name": "Hex",
          "key": "hex",
          "type": "single_line_text_field",
          "validations": [
            {
              "name": "regex",
              "value": "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
            }
          ]
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "metaobjectDefinitionCreate": {
      "metaobjectDefinition": {
        "name": "Color swatch",
        "type": "color-swatch",
        "fieldDefinitions": [
          {
            "name": "Hex",
            "key": "hex"
          }
        ]
      },
      "userErrors": []
    }
  }
  ```

* ### Create a metaobject definition with custom access controls

  #### Description

  You can create a metaobject definition with custom access controls by using the \`metaobjectDefinitionCreate\` mutation along with the \`access\` input. The following example shows how to create a metaobject definition called "FAQ" that has two fields: "Question" and "Answer". The FAQ metaobject is defined using the \`MERCHANT\_READ\_WRITE\` admin access setting and \`PUBLIC\_READ\` storefront access setting to make it read/writable within the merchant's admin and also be readable by the storefront. Note: By using the \`$app:\` prefix in the \`type\` field, the metaobject definition will be reserved for use by the app that created it and prevents other apps from modifying the definition.

  #### Query

  ```graphql
  mutation CreateMetaobjectDefinition($definition: MetaobjectDefinitionCreateInput!) {
    metaobjectDefinitionCreate(definition: $definition) {
      metaobjectDefinition {
        name
        type
        access {
          admin
          storefront
        }
        fieldDefinitions {
          name
          key
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
      "name": "FAQ",
      "type": "$app:faq",
      "access": {
        "admin": "MERCHANT_READ_WRITE",
        "storefront": "PUBLIC_READ"
      },
      "fieldDefinitions": [
        {
          "name": "Question",
          "key": "question",
          "type": "single_line_text_field",
          "validations": [
            {
              "name": "max",
              "value": "100"
            }
          ]
        },
        {
          "name": "Answer",
          "key": "answer",
          "type": "multi_line_text_field",
          "validations": [
            {
              "name": "max",
              "value": "250"
            }
          ]
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
  "query": "mutation CreateMetaobjectDefinition($definition: MetaobjectDefinitionCreateInput!) { metaobjectDefinitionCreate(definition: $definition) { metaobjectDefinition { name type access { admin storefront } fieldDefinitions { name key } } userErrors { field message code } } }",
   "variables": {
      "definition": {
        "name": "FAQ",
        "type": "$app:faq",
        "access": {
          "admin": "MERCHANT_READ_WRITE",
          "storefront": "PUBLIC_READ"
        },
        "fieldDefinitions": [
          {
            "name": "Question",
            "key": "question",
            "type": "single_line_text_field",
            "validations": [
              {
                "name": "max",
                "value": "100"
              }
            ]
          },
          {
            "name": "Answer",
            "key": "answer",
            "type": "multi_line_text_field",
            "validations": [
              {
                "name": "max",
                "value": "250"
              }
            ]
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
    mutation CreateMetaobjectDefinition($definition: MetaobjectDefinitionCreateInput!) {
      metaobjectDefinitionCreate(definition: $definition) {
        metaobjectDefinition {
          name
          type
          access {
            admin
            storefront
          }
          fieldDefinitions {
            name
            key
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
              "name": "FAQ",
              "type": "$app:faq",
              "access": {
                  "admin": "MERCHANT_READ_WRITE",
                  "storefront": "PUBLIC_READ"
              },
              "fieldDefinitions": [
                  {
                      "name": "Question",
                      "key": "question",
                      "type": "single_line_text_field",
                      "validations": [
                          {
                              "name": "max",
                              "value": "100"
                          }
                      ]
                  },
                  {
                      "name": "Answer",
                      "key": "answer",
                      "type": "multi_line_text_field",
                      "validations": [
                          {
                              "name": "max",
                              "value": "250"
                          }
                      ]
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
    mutation CreateMetaobjectDefinition($definition: MetaobjectDefinitionCreateInput!) {
      metaobjectDefinitionCreate(definition: $definition) {
        metaobjectDefinition {
          name
          type
          access {
            admin
            storefront
          }
          fieldDefinitions {
            name
            key
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
      "name": "FAQ",
      "type": "$app:faq",
      "access": {
        "admin": "MERCHANT_READ_WRITE",
        "storefront": "PUBLIC_READ"
      },
      "fieldDefinitions": [
        {
          "name": "Question",
          "key": "question",
          "type": "single_line_text_field",
          "validations": [
            {
              "name": "max",
              "value": "100"
            }
          ]
        },
        {
          "name": "Answer",
          "key": "answer",
          "type": "multi_line_text_field",
          "validations": [
            {
              "name": "max",
              "value": "250"
            }
          ]
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
      "query": `mutation CreateMetaobjectDefinition($definition: MetaobjectDefinitionCreateInput!) {
        metaobjectDefinitionCreate(definition: $definition) {
          metaobjectDefinition {
            name
            type
            access {
              admin
              storefront
            }
            fieldDefinitions {
              name
              key
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
              "name": "FAQ",
              "type": "$app:faq",
              "access": {
                  "admin": "MERCHANT_READ_WRITE",
                  "storefront": "PUBLIC_READ"
              },
              "fieldDefinitions": [
                  {
                      "name": "Question",
                      "key": "question",
                      "type": "single_line_text_field",
                      "validations": [
                          {
                              "name": "max",
                              "value": "100"
                          }
                      ]
                  },
                  {
                      "name": "Answer",
                      "key": "answer",
                      "type": "multi_line_text_field",
                      "validations": [
                          {
                              "name": "max",
                              "value": "250"
                          }
                      ]
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
  'mutation CreateMetaobjectDefinition($definition: MetaobjectDefinitionCreateInput!) {
    metaobjectDefinitionCreate(definition: $definition) {
      metaobjectDefinition {
        name
        type
        access {
          admin
          storefront
        }
        fieldDefinitions {
          name
          key
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
      "name": "FAQ",
      "type": "$app:faq",
      "access": {
        "admin": "MERCHANT_READ_WRITE",
        "storefront": "PUBLIC_READ"
      },
      "fieldDefinitions": [
        {
          "name": "Question",
          "key": "question",
          "type": "single_line_text_field",
          "validations": [
            {
              "name": "max",
              "value": "100"
            }
          ]
        },
        {
          "name": "Answer",
          "key": "answer",
          "type": "multi_line_text_field",
          "validations": [
            {
              "name": "max",
              "value": "250"
            }
          ]
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "metaobjectDefinitionCreate": {
      "metaobjectDefinition": {
        "name": "FAQ",
        "type": "app--1830279--faq",
        "access": {
          "admin": "MERCHANT_READ_WRITE",
          "storefront": "PUBLIC_READ"
        },
        "fieldDefinitions": [
          {
            "name": "Question",
            "key": "question"
          },
          {
            "name": "Answer",
            "key": "answer"
          }
        ]
      },
      "userErrors": []
    }
  }
  ```

* ### Create a metaobject definition with the publishable capability enabled

  #### Description

  Using the \`capabilities\` input, you can enable the publishable capability within your \`metaobjectDefinitionCreate\` mutation. The following example shows how to create a metaobject definition called "Custom Page" that has a "title" and "author" field. Enabling \`publishable\` provides metaobjects created with this definition a \`status\` field that can be used to stage metaobjects using \`DRAFT\` or \`ACTIVE\`.

  #### Query

  ```graphql
  mutation CreateMetaobjectDefinition($definition: MetaobjectDefinitionCreateInput!) {
    metaobjectDefinitionCreate(definition: $definition) {
      metaobjectDefinition {
        name
        type
        capabilities {
          publishable {
            enabled
          }
        }
        fieldDefinitions {
          name
          key
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
      "name": "Custom Page",
      "type": "$app:custom-page",
      "capabilities": {
        "publishable": {
          "enabled": true
        }
      },
      "fieldDefinitions": [
        {
          "name": "Title",
          "key": "title",
          "type": "single_line_text_field",
          "validations": [
            {
              "name": "max",
              "value": "100"
            }
          ]
        },
        {
          "name": "Author",
          "key": "author",
          "type": "single_line_text_field",
          "validations": [
            {
              "name": "max",
              "value": "32"
            }
          ]
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
  "query": "mutation CreateMetaobjectDefinition($definition: MetaobjectDefinitionCreateInput!) { metaobjectDefinitionCreate(definition: $definition) { metaobjectDefinition { name type capabilities { publishable { enabled } } fieldDefinitions { name key } } userErrors { field message code } } }",
   "variables": {
      "definition": {
        "name": "Custom Page",
        "type": "$app:custom-page",
        "capabilities": {
          "publishable": {
            "enabled": true
          }
        },
        "fieldDefinitions": [
          {
            "name": "Title",
            "key": "title",
            "type": "single_line_text_field",
            "validations": [
              {
                "name": "max",
                "value": "100"
              }
            ]
          },
          {
            "name": "Author",
            "key": "author",
            "type": "single_line_text_field",
            "validations": [
              {
                "name": "max",
                "value": "32"
              }
            ]
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
    mutation CreateMetaobjectDefinition($definition: MetaobjectDefinitionCreateInput!) {
      metaobjectDefinitionCreate(definition: $definition) {
        metaobjectDefinition {
          name
          type
          capabilities {
            publishable {
              enabled
            }
          }
          fieldDefinitions {
            name
            key
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
              "name": "Custom Page",
              "type": "$app:custom-page",
              "capabilities": {
                  "publishable": {
                      "enabled": true
                  }
              },
              "fieldDefinitions": [
                  {
                      "name": "Title",
                      "key": "title",
                      "type": "single_line_text_field",
                      "validations": [
                          {
                              "name": "max",
                              "value": "100"
                          }
                      ]
                  },
                  {
                      "name": "Author",
                      "key": "author",
                      "type": "single_line_text_field",
                      "validations": [
                          {
                              "name": "max",
                              "value": "32"
                          }
                      ]
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
    mutation CreateMetaobjectDefinition($definition: MetaobjectDefinitionCreateInput!) {
      metaobjectDefinitionCreate(definition: $definition) {
        metaobjectDefinition {
          name
          type
          capabilities {
            publishable {
              enabled
            }
          }
          fieldDefinitions {
            name
            key
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
      "name": "Custom Page",
      "type": "$app:custom-page",
      "capabilities": {
        "publishable": {
          "enabled": true
        }
      },
      "fieldDefinitions": [
        {
          "name": "Title",
          "key": "title",
          "type": "single_line_text_field",
          "validations": [
            {
              "name": "max",
              "value": "100"
            }
          ]
        },
        {
          "name": "Author",
          "key": "author",
          "type": "single_line_text_field",
          "validations": [
            {
              "name": "max",
              "value": "32"
            }
          ]
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
      "query": `mutation CreateMetaobjectDefinition($definition: MetaobjectDefinitionCreateInput!) {
        metaobjectDefinitionCreate(definition: $definition) {
          metaobjectDefinition {
            name
            type
            capabilities {
              publishable {
                enabled
              }
            }
            fieldDefinitions {
              name
              key
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
              "name": "Custom Page",
              "type": "$app:custom-page",
              "capabilities": {
                  "publishable": {
                      "enabled": true
                  }
              },
              "fieldDefinitions": [
                  {
                      "name": "Title",
                      "key": "title",
                      "type": "single_line_text_field",
                      "validations": [
                          {
                              "name": "max",
                              "value": "100"
                          }
                      ]
                  },
                  {
                      "name": "Author",
                      "key": "author",
                      "type": "single_line_text_field",
                      "validations": [
                          {
                              "name": "max",
                              "value": "32"
                          }
                      ]
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
  'mutation CreateMetaobjectDefinition($definition: MetaobjectDefinitionCreateInput!) {
    metaobjectDefinitionCreate(definition: $definition) {
      metaobjectDefinition {
        name
        type
        capabilities {
          publishable {
            enabled
          }
        }
        fieldDefinitions {
          name
          key
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
      "name": "Custom Page",
      "type": "$app:custom-page",
      "capabilities": {
        "publishable": {
          "enabled": true
        }
      },
      "fieldDefinitions": [
        {
          "name": "Title",
          "key": "title",
          "type": "single_line_text_field",
          "validations": [
            {
              "name": "max",
              "value": "100"
            }
          ]
        },
        {
          "name": "Author",
          "key": "author",
          "type": "single_line_text_field",
          "validations": [
            {
              "name": "max",
              "value": "32"
            }
          ]
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "metaobjectDefinitionCreate": {
      "metaobjectDefinition": {
        "name": "Custom Page",
        "type": "app--1830279--custom-page",
        "capabilities": {
          "publishable": {
            "enabled": true
          }
        },
        "fieldDefinitions": [
          {
            "name": "Title",
            "key": "title"
          },
          {
            "name": "Author",
            "key": "author"
          }
        ]
      },
      "userErrors": []
    }
  }
  ```

* ### metaobjectDefinitionCreate reference
