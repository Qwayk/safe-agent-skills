---
title: themeFilesCopy - GraphQL Admin
description: Copy theme files. Copying to existing theme files will overwrite them.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/themeFilesCopy'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/themeFilesCopy.md
---

# theme​Files​Copy

mutation

Requires The user needs write\_themes and an exemption from Shopify to modify theme files. If you think that your app is eligible for an exemption and should have access to this API, then you can [submit an exception request](https://docs.google.com/forms/d/e/1FAIpQLSfZTB1vxFC5d1-GPdqYunWRGUoDcOheHQzfK2RoEFEHrknt5g/viewform).

Copy theme files. Copying to existing theme files will overwrite them.

## Arguments

* files

  [\[Theme​Files​Copy​File​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ThemeFilesCopyFileInput)

  required

  The files to update.

* theme​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The theme to update.

***

## Theme​Files​Copy​Payload returns

* copied​Theme​Files

  [\[Online​Store​Theme​File​Operation​Result!\]](https://shopify.dev/docs/api/admin-graphql/latest/objects/OnlineStoreThemeFileOperationResult)

  The resulting theme files.

* user​Errors

  [\[Online​Store​Theme​Files​User​Errors!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/OnlineStoreThemeFilesUserErrors)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Copy the content of a file into another file

  #### Query

  ```graphql
  mutation themeFilesCopy($files: [ThemeFilesCopyFileInput!]!, $themeId: ID!) {
    themeFilesCopy(files: $files, themeId: $themeId) {
      copiedThemeFiles {
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
      {
        "dstFilename": "templates/index.alt.json",
        "srcFilename": "templates/index.json"
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
  "query": "mutation themeFilesCopy($files: [ThemeFilesCopyFileInput!]!, $themeId: ID!) { themeFilesCopy(files: $files, themeId: $themeId) { copiedThemeFiles { filename } userErrors { field message } } }",
   "variables": {
      "themeId": "gid://shopify/OnlineStoreTheme/529529152",
      "files": [
        {
          "dstFilename": "templates/index.alt.json",
          "srcFilename": "templates/index.json"
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
    mutation themeFilesCopy($files: [ThemeFilesCopyFileInput!]!, $themeId: ID!) {
      themeFilesCopy(files: $files, themeId: $themeId) {
        copiedThemeFiles {
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
              {
                  "dstFilename": "templates/index.alt.json",
                  "srcFilename": "templates/index.json"
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
    mutation themeFilesCopy($files: [ThemeFilesCopyFileInput!]!, $themeId: ID!) {
      themeFilesCopy(files: $files, themeId: $themeId) {
        copiedThemeFiles {
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
      {
        "dstFilename": "templates/index.alt.json",
        "srcFilename": "templates/index.json"
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
      "query": `mutation themeFilesCopy($files: [ThemeFilesCopyFileInput!]!, $themeId: ID!) {
        themeFilesCopy(files: $files, themeId: $themeId) {
          copiedThemeFiles {
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
              {
                  "dstFilename": "templates/index.alt.json",
                  "srcFilename": "templates/index.json"
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
  'mutation themeFilesCopy($files: [ThemeFilesCopyFileInput!]!, $themeId: ID!) {
    themeFilesCopy(files: $files, themeId: $themeId) {
      copiedThemeFiles {
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
      {
        "dstFilename": "templates/index.alt.json",
        "srcFilename": "templates/index.json"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "themeFilesCopy": {
      "copiedThemeFiles": [
        {
          "filename": "templates/index.alt.json"
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### Creates or updates an asset for a theme

  #### Query

  ```graphql
  mutation ThemeFilesCopy($files: [ThemeFilesCopyFileInput!]!, $themeId: ID!) {
    themeFilesCopy(files: $files, themeId: $themeId) {
      copiedThemeFiles {
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
      {
        "dstFilename": "templates/index.alt.liquid",
        "srcFilename": "templates/index.liquid"
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
  "query": "mutation ThemeFilesCopy($files: [ThemeFilesCopyFileInput!]!, $themeId: ID!) { themeFilesCopy(files: $files, themeId: $themeId) { copiedThemeFiles { filename } userErrors { code field filename message } } }",
   "variables": {
      "themeId": "gid://shopify/OnlineStoreTheme/529529152",
      "files": [
        {
          "dstFilename": "templates/index.alt.liquid",
          "srcFilename": "templates/index.liquid"
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
    mutation ThemeFilesCopy($files: [ThemeFilesCopyFileInput!]!, $themeId: ID!) {
      themeFilesCopy(files: $files, themeId: $themeId) {
        copiedThemeFiles {
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
              {
                  "dstFilename": "templates/index.alt.liquid",
                  "srcFilename": "templates/index.liquid"
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
    mutation ThemeFilesCopy($files: [ThemeFilesCopyFileInput!]!, $themeId: ID!) {
      themeFilesCopy(files: $files, themeId: $themeId) {
        copiedThemeFiles {
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
      {
        "dstFilename": "templates/index.alt.liquid",
        "srcFilename": "templates/index.liquid"
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
      "query": `mutation ThemeFilesCopy($files: [ThemeFilesCopyFileInput!]!, $themeId: ID!) {
        themeFilesCopy(files: $files, themeId: $themeId) {
          copiedThemeFiles {
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
              {
                  "dstFilename": "templates/index.alt.liquid",
                  "srcFilename": "templates/index.liquid"
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
  'mutation ThemeFilesCopy($files: [ThemeFilesCopyFileInput!]!, $themeId: ID!) {
    themeFilesCopy(files: $files, themeId: $themeId) {
      copiedThemeFiles {
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
      {
        "dstFilename": "templates/index.alt.liquid",
        "srcFilename": "templates/index.liquid"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "themeFilesCopy": {
      "copiedThemeFiles": [
        {
          "filename": "templates/index.alt.liquid"
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### themeFilesCopy reference
