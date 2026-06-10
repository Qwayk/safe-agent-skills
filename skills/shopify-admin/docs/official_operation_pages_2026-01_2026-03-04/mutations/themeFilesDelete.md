---
title: themeFilesDelete - GraphQL Admin
description: Deletes a theme's files.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/themeFilesDelete'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/themeFilesDelete.md
---

# theme​Files​Delete

mutation

Requires The user needs write\_themes and an exemption from Shopify to modify theme files. If you think that your app is eligible for an exemption and should have access to this API, then you can [submit an exception request](https://docs.google.com/forms/d/e/1FAIpQLSfZTB1vxFC5d1-GPdqYunWRGUoDcOheHQzfK2RoEFEHrknt5g/viewform).

Deletes a theme's files.

## Arguments

* files

  [\[String!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  The files to delete.

* theme​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  Specifies the theme to deleted.

***

## Theme​Files​Delete​Payload returns

* deleted​Theme​Files

  [\[Online​Store​Theme​File​Operation​Result!\]](https://shopify.dev/docs/api/admin-graphql/latest/objects/OnlineStoreThemeFileOperationResult)

  The resulting theme files.

* user​Errors

  [\[Online​Store​Theme​Files​User​Errors!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/OnlineStoreThemeFilesUserErrors)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Delete a theme file

  #### Query

  ```graphql
  mutation themeFilesDelete($themeId: ID!, $files: [String!]!) {
    themeFilesDelete(themeId: $themeId, files: $files) {
      deletedThemeFiles {
        filename
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
    "themeId": "gid://shopify/OnlineStoreTheme/529529152",
    "files": [
      "templates/index.json"
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
  "query": "mutation themeFilesDelete($themeId: ID!, $files: [String!]!) { themeFilesDelete(themeId: $themeId, files: $files) { deletedThemeFiles { filename } userErrors { field message } } }",
   "variables": {
      "themeId": "gid://shopify/OnlineStoreTheme/529529152",
      "files": [
        "templates/index.json"
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
    mutation themeFilesDelete($themeId: ID!, $files: [String!]!) {
      themeFilesDelete(themeId: $themeId, files: $files) {
        deletedThemeFiles {
          filename
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "themeId": "gid://shopify/OnlineStoreTheme/529529152",
          "files": [
              "templates/index.json"
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
    mutation themeFilesDelete($themeId: ID!, $files: [String!]!) {
      themeFilesDelete(themeId: $themeId, files: $files) {
        deletedThemeFiles {
          filename
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "themeId": "gid://shopify/OnlineStoreTheme/529529152",
    "files": [
      "templates/index.json"
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation themeFilesDelete($themeId: ID!, $files: [String!]!) {
        themeFilesDelete(themeId: $themeId, files: $files) {
          deletedThemeFiles {
            filename
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "themeId": "gid://shopify/OnlineStoreTheme/529529152",
          "files": [
              "templates/index.json"
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation themeFilesDelete($themeId: ID!, $files: [String!]!) {
    themeFilesDelete(themeId: $themeId, files: $files) {
      deletedThemeFiles {
        filename
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "themeId": "gid://shopify/OnlineStoreTheme/529529152",
    "files": [
      "templates/index.json"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "themeFilesDelete": {
      "deletedThemeFiles": [
        {
          "filename": "templates/index.json"
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### Deletes an asset from a theme

  #### Query

  ```graphql
  mutation ThemeFilesDelete($files: [String!]!, $themeId: ID!) {
    themeFilesDelete(files: $files, themeId: $themeId) {
      deletedThemeFiles {
        filename
      }
      userErrors {
        code
        field
        filename
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "themeId": "gid://shopify/OnlineStoreTheme/529529152",
    "files": [
      "sections/content_section.liquid"
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
  "query": "mutation ThemeFilesDelete($files: [String!]!, $themeId: ID!) { themeFilesDelete(files: $files, themeId: $themeId) { deletedThemeFiles { filename } userErrors { code field filename message } } }",
   "variables": {
      "themeId": "gid://shopify/OnlineStoreTheme/529529152",
      "files": [
        "sections/content_section.liquid"
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
    mutation ThemeFilesDelete($files: [String!]!, $themeId: ID!) {
      themeFilesDelete(files: $files, themeId: $themeId) {
        deletedThemeFiles {
          filename
        }
        userErrors {
          code
          field
          filename
          message
        }
      }
    }`,
    {
      variables: {
          "themeId": "gid://shopify/OnlineStoreTheme/529529152",
          "files": [
              "sections/content_section.liquid"
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
    mutation ThemeFilesDelete($files: [String!]!, $themeId: ID!) {
      themeFilesDelete(files: $files, themeId: $themeId) {
        deletedThemeFiles {
          filename
        }
        userErrors {
          code
          field
          filename
          message
        }
      }
    }
  QUERY

  variables = {
    "themeId": "gid://shopify/OnlineStoreTheme/529529152",
    "files": [
      "sections/content_section.liquid"
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation ThemeFilesDelete($files: [String!]!, $themeId: ID!) {
        themeFilesDelete(files: $files, themeId: $themeId) {
          deletedThemeFiles {
            filename
          }
          userErrors {
            code
            field
            filename
            message
          }
        }
      }`,
      "variables": {
          "themeId": "gid://shopify/OnlineStoreTheme/529529152",
          "files": [
              "sections/content_section.liquid"
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation ThemeFilesDelete($files: [String!]!, $themeId: ID!) {
    themeFilesDelete(files: $files, themeId: $themeId) {
      deletedThemeFiles {
        filename
      }
      userErrors {
        code
        field
        filename
        message
      }
    }
  }' \
  --variables \
  '{
    "themeId": "gid://shopify/OnlineStoreTheme/529529152",
    "files": [
      "sections/content_section.liquid"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "themeFilesDelete": {
      "deletedThemeFiles": [
        {
          "filename": "sections/content_section.liquid"
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### themeFilesDelete reference
