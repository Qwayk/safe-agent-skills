---
title: metaobjectDefinitionUpdate - GraphQL Admin
description: >-
  Updates a
  [`MetaobjectDefinition`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectDefinition)'s
  configuration and field structure. You can modify the definition's name,
  description, display name key, access controls, and capabilities, as well as
  those of all its fields.


  The mutation supports reordering fields when `resetFieldOrder` is `true`,
  which arranges submitted fields first followed by alphabetized omitted fields.


  Learn more about [managing
  metaobjects](https://shopify.dev/docs/apps/build/custom-data/metaobjects/manage-metaobjects).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/metaobjectDefinitionUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/metaobjectDefinitionUpdate.md
---

# metaobject​Definition​Update

mutation

Requires `write_metaobject_definitions` access scope.

Updates a [`MetaobjectDefinition`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectDefinition)'s configuration and field structure. You can modify the definition's name, description, display name key, access controls, and capabilities, as well as those of all its fields.

The mutation supports reordering fields when `resetFieldOrder` is `true`, which arranges submitted fields first followed by alphabetized omitted fields.

Learn more about [managing metaobjects](https://shopify.dev/docs/apps/build/custom-data/metaobjects/manage-metaobjects).

## Arguments

* definition

  [Metaobject​Definition​Update​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MetaobjectDefinitionUpdateInput)

  required

  The input fields for updating a metaobject definition.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the metaobject definition to update.

***

## Metaobject​Definition​Update​Payload returns

* metaobject​Definition

  [Metaobject​Definition](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectDefinition)

  The updated metaobject definition.

* user​Errors

  [\[Metaobject​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create additional field definitions on an existing metaobject definition

  #### Description

  To add a field definition to an existing metaobject definition, use the \`metaobjectDefinitionUpdate\` mutation with the \`create\` \`MetaobjectFieldDefinitionOperationInput\`. The following example shows adding a new field definition named "Description" to the "LookBook" metaobject definition.

  #### Query

  ```graphql
  mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) {
    metaobjectDefinitionUpdate(id: $id, definition: $definition) {
      metaobjectDefinition {
        id
        name
        displayNameKey
        fieldDefinitions {
          name
          key
          type {
            name
          }
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
    "id": "gid://shopify/MetaobjectDefinition/578408816",
    "definition": {
      "displayNameKey": "description",
      "fieldDefinitions": [
        {
          "create": {
            "key": "description",
            "name": "Description",
            "type": "single_line_text_field"
          }
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
  "query": "mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) { metaobjectDefinitionUpdate(id: $id, definition: $definition) { metaobjectDefinition { id name displayNameKey fieldDefinitions { name key type { name } } } userErrors { field message code } } }",
   "variables": {
      "id": "gid://shopify/MetaobjectDefinition/578408816",
      "definition": {
        "displayNameKey": "description",
        "fieldDefinitions": [
          {
            "create": {
              "key": "description",
              "name": "Description",
              "type": "single_line_text_field"
            }
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
    mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) {
      metaobjectDefinitionUpdate(id: $id, definition: $definition) {
        metaobjectDefinition {
          id
          name
          displayNameKey
          fieldDefinitions {
            name
            key
            type {
              name
            }
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
          "id": "gid://shopify/MetaobjectDefinition/578408816",
          "definition": {
              "displayNameKey": "description",
              "fieldDefinitions": [
                  {
                      "create": {
                          "key": "description",
                          "name": "Description",
                          "type": "single_line_text_field"
                      }
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
    mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) {
      metaobjectDefinitionUpdate(id: $id, definition: $definition) {
        metaobjectDefinition {
          id
          name
          displayNameKey
          fieldDefinitions {
            name
            key
            type {
              name
            }
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
    "id": "gid://shopify/MetaobjectDefinition/578408816",
    "definition": {
      "displayNameKey": "description",
      "fieldDefinitions": [
        {
          "create": {
            "key": "description",
            "name": "Description",
            "type": "single_line_text_field"
          }
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
      "query": `mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) {
        metaobjectDefinitionUpdate(id: $id, definition: $definition) {
          metaobjectDefinition {
            id
            name
            displayNameKey
            fieldDefinitions {
              name
              key
              type {
                name
              }
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
          "id": "gid://shopify/MetaobjectDefinition/578408816",
          "definition": {
              "displayNameKey": "description",
              "fieldDefinitions": [
                  {
                      "create": {
                          "key": "description",
                          "name": "Description",
                          "type": "single_line_text_field"
                      }
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
  'mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) {
    metaobjectDefinitionUpdate(id: $id, definition: $definition) {
      metaobjectDefinition {
        id
        name
        displayNameKey
        fieldDefinitions {
          name
          key
          type {
            name
          }
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
    "id": "gid://shopify/MetaobjectDefinition/578408816",
    "definition": {
      "displayNameKey": "description",
      "fieldDefinitions": [
        {
          "create": {
            "key": "description",
            "name": "Description",
            "type": "single_line_text_field"
          }
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "metaobjectDefinitionUpdate": {
      "metaobjectDefinition": {
        "id": "gid://shopify/MetaobjectDefinition/578408816",
        "name": "LookBook",
        "displayNameKey": "description",
        "fieldDefinitions": [
          {
            "name": "Another Lookbook",
            "key": "another_lookbook",
            "type": {
              "name": "metaobject_reference"
            }
          },
          {
            "name": "Season",
            "key": "cover_image",
            "type": {
              "name": "file_reference"
            }
          },
          {
            "name": "Season",
            "key": "season",
            "type": {
              "name": "single_line_text_field"
            }
          },
          {
            "name": "Year",
            "key": "year",
            "type": {
              "name": "number_integer"
            }
          },
          {
            "name": "Description",
            "key": "description",
            "type": {
              "name": "single_line_text_field"
            }
          }
        ]
      },
      "userErrors": []
    }
  }
  ```

* ### Delete a field definition from a metaobject definition

  #### Description

  To delete a field definition from an existing metaobject definnition, use the \`metaobjectDefinitionUpdate\` mutation with the \`delete\` \`MetaobjectFieldDefinitionOperationInput\`. The following example shows deleting the "Season" field definition on "Lookbook".

  #### Query

  ```graphql
  mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) {
    metaobjectDefinitionUpdate(id: $id, definition: $definition) {
      metaobjectDefinition {
        id
        name
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
    "id": "gid://shopify/MetaobjectDefinition/578408816",
    "definition": {
      "fieldDefinitions": [
        {
          "delete": {
            "key": "season"
          }
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
  "query": "mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) { metaobjectDefinitionUpdate(id: $id, definition: $definition) { metaobjectDefinition { id name fieldDefinitions { name key } } userErrors { field message code } } }",
   "variables": {
      "id": "gid://shopify/MetaobjectDefinition/578408816",
      "definition": {
        "fieldDefinitions": [
          {
            "delete": {
              "key": "season"
            }
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
    mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) {
      metaobjectDefinitionUpdate(id: $id, definition: $definition) {
        metaobjectDefinition {
          id
          name
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
          "id": "gid://shopify/MetaobjectDefinition/578408816",
          "definition": {
              "fieldDefinitions": [
                  {
                      "delete": {
                          "key": "season"
                      }
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
    mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) {
      metaobjectDefinitionUpdate(id: $id, definition: $definition) {
        metaobjectDefinition {
          id
          name
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
    "id": "gid://shopify/MetaobjectDefinition/578408816",
    "definition": {
      "fieldDefinitions": [
        {
          "delete": {
            "key": "season"
          }
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
      "query": `mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) {
        metaobjectDefinitionUpdate(id: $id, definition: $definition) {
          metaobjectDefinition {
            id
            name
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
          "id": "gid://shopify/MetaobjectDefinition/578408816",
          "definition": {
              "fieldDefinitions": [
                  {
                      "delete": {
                          "key": "season"
                      }
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
  'mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) {
    metaobjectDefinitionUpdate(id: $id, definition: $definition) {
      metaobjectDefinition {
        id
        name
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
    "id": "gid://shopify/MetaobjectDefinition/578408816",
    "definition": {
      "fieldDefinitions": [
        {
          "delete": {
            "key": "season"
          }
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "metaobjectDefinitionUpdate": {
      "metaobjectDefinition": {
        "id": "gid://shopify/MetaobjectDefinition/578408816",
        "name": "LookBook",
        "fieldDefinitions": [
          {
            "name": "Another Lookbook",
            "key": "another_lookbook"
          },
          {
            "name": "Season",
            "key": "cover_image"
          },
          {
            "name": "Year",
            "key": "year"
          }
        ]
      },
      "userErrors": []
    }
  }
  ```

* ### Update an existing field definition on a metaobject definition

  #### Description

  To update a field definition on an existing metaobject, use the \`metaobjectDefinitionUpdate\` mutation with the \`update\` \`MetaobjectFieldDefinitionOperationInput\`. The following example shows updating the name of the "Season" field definition on the "Lookbook" metaobject definition to be "Edition".

  #### Query

  ```graphql
  mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) {
    metaobjectDefinitionUpdate(id: $id, definition: $definition) {
      metaobjectDefinition {
        name
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
    "id": "gid://shopify/MetaobjectDefinition/578408816",
    "definition": {
      "fieldDefinitions": [
        {
          "update": {
            "key": "season",
            "name": "Edition"
          }
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
  "query": "mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) { metaobjectDefinitionUpdate(id: $id, definition: $definition) { metaobjectDefinition { name fieldDefinitions { name key } } userErrors { field message code } } }",
   "variables": {
      "id": "gid://shopify/MetaobjectDefinition/578408816",
      "definition": {
        "fieldDefinitions": [
          {
            "update": {
              "key": "season",
              "name": "Edition"
            }
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
    mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) {
      metaobjectDefinitionUpdate(id: $id, definition: $definition) {
        metaobjectDefinition {
          name
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
          "id": "gid://shopify/MetaobjectDefinition/578408816",
          "definition": {
              "fieldDefinitions": [
                  {
                      "update": {
                          "key": "season",
                          "name": "Edition"
                      }
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
    mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) {
      metaobjectDefinitionUpdate(id: $id, definition: $definition) {
        metaobjectDefinition {
          name
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
    "id": "gid://shopify/MetaobjectDefinition/578408816",
    "definition": {
      "fieldDefinitions": [
        {
          "update": {
            "key": "season",
            "name": "Edition"
          }
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
      "query": `mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) {
        metaobjectDefinitionUpdate(id: $id, definition: $definition) {
          metaobjectDefinition {
            name
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
          "id": "gid://shopify/MetaobjectDefinition/578408816",
          "definition": {
              "fieldDefinitions": [
                  {
                      "update": {
                          "key": "season",
                          "name": "Edition"
                      }
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
  'mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) {
    metaobjectDefinitionUpdate(id: $id, definition: $definition) {
      metaobjectDefinition {
        name
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
    "id": "gid://shopify/MetaobjectDefinition/578408816",
    "definition": {
      "fieldDefinitions": [
        {
          "update": {
            "key": "season",
            "name": "Edition"
          }
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "metaobjectDefinitionUpdate": {
      "metaobjectDefinition": {
        "name": "LookBook",
        "fieldDefinitions": [
          {
            "name": "Another Lookbook",
            "key": "another_lookbook"
          },
          {
            "name": "Season",
            "key": "cover_image"
          },
          {
            "name": "Edition",
            "key": "season"
          },
          {
            "name": "Year",
            "key": "year"
          }
        ]
      },
      "userErrors": []
    }
  }
  ```

* ### Update base attributes of a metaobject definition

  #### Description

  To update a metaobject definition, use the \`metaobjectDefinitionUpdate\` mutation. The following example shows updating the name of the metaobject definition "Lookbook" to "Stylebook" and changing the display name key to "season".

  #### Query

  ```graphql
  mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) {
    metaobjectDefinitionUpdate(id: $id, definition: $definition) {
      metaobjectDefinition {
        id
        name
        displayNameKey
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
    "id": "gid://shopify/MetaobjectDefinition/578408816",
    "definition": {
      "name": "StyleBook",
      "displayNameKey": "season"
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
  "query": "mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) { metaobjectDefinitionUpdate(id: $id, definition: $definition) { metaobjectDefinition { id name displayNameKey } userErrors { field message code } } }",
   "variables": {
      "id": "gid://shopify/MetaobjectDefinition/578408816",
      "definition": {
        "name": "StyleBook",
        "displayNameKey": "season"
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
    mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) {
      metaobjectDefinitionUpdate(id: $id, definition: $definition) {
        metaobjectDefinition {
          id
          name
          displayNameKey
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
          "id": "gid://shopify/MetaobjectDefinition/578408816",
          "definition": {
              "name": "StyleBook",
              "displayNameKey": "season"
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
    mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) {
      metaobjectDefinitionUpdate(id: $id, definition: $definition) {
        metaobjectDefinition {
          id
          name
          displayNameKey
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
    "id": "gid://shopify/MetaobjectDefinition/578408816",
    "definition": {
      "name": "StyleBook",
      "displayNameKey": "season"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) {
        metaobjectDefinitionUpdate(id: $id, definition: $definition) {
          metaobjectDefinition {
            id
            name
            displayNameKey
          }
          userErrors {
            field
            message
            code
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/MetaobjectDefinition/578408816",
          "definition": {
              "name": "StyleBook",
              "displayNameKey": "season"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) {
    metaobjectDefinitionUpdate(id: $id, definition: $definition) {
      metaobjectDefinition {
        id
        name
        displayNameKey
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
    "id": "gid://shopify/MetaobjectDefinition/578408816",
    "definition": {
      "name": "StyleBook",
      "displayNameKey": "season"
    }
  }'
  ```

  #### Response

  ```json
  {
    "metaobjectDefinitionUpdate": {
      "metaobjectDefinition": {
        "id": "gid://shopify/MetaobjectDefinition/578408816",
        "name": "StyleBook",
        "displayNameKey": "season"
      },
      "userErrors": []
    }
  }
  ```

* ### Update ordering of fields on an existing metaobject definition

  #### Description

  To update the ordering of fields on an existing metaobject definition, use the \`metaobjectDefinitionUpdate\` mutation with the \`resetFieldOrder\` boolean. The following example shows updating the ordering of the fields on the "Color" metaobject definition. Prior to the update, the ordering of the fields is "name", "hex", "accent\_color". After the update, the ordering changes to "hex", "name", and "accent\_color".

  #### Query

  ```graphql
  mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) {
    metaobjectDefinitionUpdate(id: $id, definition: $definition) {
      metaobjectDefinition {
        id
        name
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
    "id": "gid://shopify/MetaobjectDefinition/228758553",
    "definition": {
      "resetFieldOrder": true,
      "fieldDefinitions": [
        {
          "update": {
            "key": "hex"
          }
        },
        {
          "update": {
            "key": "name"
          }
        },
        {
          "update": {
            "key": "accent_color"
          }
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
  "query": "mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) { metaobjectDefinitionUpdate(id: $id, definition: $definition) { metaobjectDefinition { id name fieldDefinitions { name key } } userErrors { field message code } } }",
   "variables": {
      "id": "gid://shopify/MetaobjectDefinition/228758553",
      "definition": {
        "resetFieldOrder": true,
        "fieldDefinitions": [
          {
            "update": {
              "key": "hex"
            }
          },
          {
            "update": {
              "key": "name"
            }
          },
          {
            "update": {
              "key": "accent_color"
            }
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
    mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) {
      metaobjectDefinitionUpdate(id: $id, definition: $definition) {
        metaobjectDefinition {
          id
          name
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
          "id": "gid://shopify/MetaobjectDefinition/228758553",
          "definition": {
              "resetFieldOrder": true,
              "fieldDefinitions": [
                  {
                      "update": {
                          "key": "hex"
                      }
                  },
                  {
                      "update": {
                          "key": "name"
                      }
                  },
                  {
                      "update": {
                          "key": "accent_color"
                      }
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
    mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) {
      metaobjectDefinitionUpdate(id: $id, definition: $definition) {
        metaobjectDefinition {
          id
          name
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
    "id": "gid://shopify/MetaobjectDefinition/228758553",
    "definition": {
      "resetFieldOrder": true,
      "fieldDefinitions": [
        {
          "update": {
            "key": "hex"
          }
        },
        {
          "update": {
            "key": "name"
          }
        },
        {
          "update": {
            "key": "accent_color"
          }
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
      "query": `mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) {
        metaobjectDefinitionUpdate(id: $id, definition: $definition) {
          metaobjectDefinition {
            id
            name
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
          "id": "gid://shopify/MetaobjectDefinition/228758553",
          "definition": {
              "resetFieldOrder": true,
              "fieldDefinitions": [
                  {
                      "update": {
                          "key": "hex"
                      }
                  },
                  {
                      "update": {
                          "key": "name"
                      }
                  },
                  {
                      "update": {
                          "key": "accent_color"
                      }
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
  'mutation UpdateMetaobjectDefinition($id: ID!, $definition: MetaobjectDefinitionUpdateInput!) {
    metaobjectDefinitionUpdate(id: $id, definition: $definition) {
      metaobjectDefinition {
        id
        name
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
    "id": "gid://shopify/MetaobjectDefinition/228758553",
    "definition": {
      "resetFieldOrder": true,
      "fieldDefinitions": [
        {
          "update": {
            "key": "hex"
          }
        },
        {
          "update": {
            "key": "name"
          }
        },
        {
          "update": {
            "key": "accent_color"
          }
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "metaobjectDefinitionUpdate": {
      "metaobjectDefinition": {
        "id": "gid://shopify/MetaobjectDefinition/228758553",
        "name": "Color",
        "fieldDefinitions": [
          {
            "name": "Hex code",
            "key": "hex"
          },
          {
            "name": "Name",
            "key": "name"
          },
          {
            "name": "Accent color",
            "key": "accent_color"
          },
          {
            "name": "Related colors",
            "key": "related_colors"
          },
          {
            "name": "Secondary Hex code",
            "key": "secondary_hex"
          }
        ]
      },
      "userErrors": []
    }
  }
  ```

* ### metaobjectDefinitionUpdate reference
