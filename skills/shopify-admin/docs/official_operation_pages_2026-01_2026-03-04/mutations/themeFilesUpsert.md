---
title: themeFilesUpsert - GraphQL Admin
description: >-
  Creates or updates theme files in an online store theme. This mutation allows
  batch operations on multiple theme files, either creating new files or
  overwriting existing ones with the same filename.


  > Note: You can process a maximum of 50 files in a single request.


  Each file requires a filename and body content. The body must specify a
  [`type`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/themeFilesUpsert#arguments-files.fields.body.type)
  with the corresponding
  [`value`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/themeFilesUpsert#arguments-files.fields.body.value).
  The mutation returns a
  [`job`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/themeFilesUpsert#returns-job)
  field for tracking asynchronous operations and an
  [`upsertedThemeFiles`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/themeFilesUpsert#returns-upsertedThemeFiles)
  field with details about the processed files.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/themeFilesUpsert'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/themeFilesUpsert.md
---

# theme​Files​Upsert

mutation

Requires The user needs write\_themes and an exemption from Shopify to modify theme files. If you think that your app is eligible for an exemption and should have access to this API, then you can [submit an exception request](https://docs.google.com/forms/d/e/1FAIpQLSfZTB1vxFC5d1-GPdqYunWRGUoDcOheHQzfK2RoEFEHrknt5g/viewform).

Creates or updates theme files in an online store theme. This mutation allows batch operations on multiple theme files, either creating new files or overwriting existing ones with the same filename.

***

**Note:** You can process a maximum of 50 files in a single request.

***

Each file requires a filename and body content. The body must specify a [`type`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/themeFilesUpsert#arguments-files.fields.body.type) with the corresponding [`value`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/themeFilesUpsert#arguments-files.fields.body.value). The mutation returns a [`job`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/themeFilesUpsert#returns-job) field for tracking asynchronous operations and an [`upsertedThemeFiles`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/themeFilesUpsert#returns-upsertedThemeFiles) field with details about the processed files.

## Arguments

* files

  [\[Online​Store​Theme​Files​Upsert​File​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/OnlineStoreThemeFilesUpsertFileInput)

  required

  The files to update.

* theme​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The theme to update.

***

## Theme​Files​Upsert​Payload returns

* job

  [Job](https://shopify.dev/docs/api/admin-graphql/latest/objects/Job)

  The theme files write job triggered by the mutation.

* upserted​Theme​Files

  [\[Online​Store​Theme​File​Operation​Result!\]](https://shopify.dev/docs/api/admin-graphql/latest/objects/OnlineStoreThemeFileOperationResult)

  The resulting theme files.

* user​Errors

  [\[Online​Store​Theme​Files​User​Errors!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/OnlineStoreThemeFilesUserErrors)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create or update a theme file

  #### Query

  ```graphql
  mutation themeFilesUpsert($files: [OnlineStoreThemeFilesUpsertFileInput!]!, $themeId: ID!) {
    themeFilesUpsert(files: $files, themeId: $themeId) {
      upsertedThemeFiles {
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
        "filename": "templates/index.json",
        "body": {
          "type": "TEXT",
          "value": "{ \"sections\": {}, \"order\": [] }"
        }
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
  "query": "mutation themeFilesUpsert($files: [OnlineStoreThemeFilesUpsertFileInput!]!, $themeId: ID!) { themeFilesUpsert(files: $files, themeId: $themeId) { upsertedThemeFiles { filename } userErrors { field message } } }",
   "variables": {
      "themeId": "gid://shopify/OnlineStoreTheme/529529152",
      "files": [
        {
          "filename": "templates/index.json",
          "body": {
            "type": "TEXT",
            "value": "{ \"sections\": {}, \"order\": [] }"
          }
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
    mutation themeFilesUpsert($files: [OnlineStoreThemeFilesUpsertFileInput!]!, $themeId: ID!) {
      themeFilesUpsert(files: $files, themeId: $themeId) {
        upsertedThemeFiles {
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
                  "filename": "templates/index.json",
                  "body": {
                      "type": "TEXT",
                      "value": "{ \"sections\": {}, \"order\": [] }"
                  }
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
    mutation themeFilesUpsert($files: [OnlineStoreThemeFilesUpsertFileInput!]!, $themeId: ID!) {
      themeFilesUpsert(files: $files, themeId: $themeId) {
        upsertedThemeFiles {
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
        "filename": "templates/index.json",
        "body": {
          "type": "TEXT",
          "value": "{ \"sections\": {}, \"order\": [] }"
        }
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
      "query": `mutation themeFilesUpsert($files: [OnlineStoreThemeFilesUpsertFileInput!]!, $themeId: ID!) {
        themeFilesUpsert(files: $files, themeId: $themeId) {
          upsertedThemeFiles {
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
                  "filename": "templates/index.json",
                  "body": {
                      "type": "TEXT",
                      "value": "{ \"sections\": {}, \"order\": [] }"
                  }
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
  'mutation themeFilesUpsert($files: [OnlineStoreThemeFilesUpsertFileInput!]!, $themeId: ID!) {
    themeFilesUpsert(files: $files, themeId: $themeId) {
      upsertedThemeFiles {
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
        "filename": "templates/index.json",
        "body": {
          "type": "TEXT",
          "value": "{ \"sections\": {}, \"order\": [] }"
        }
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "themeFilesUpsert": {
      "upsertedThemeFiles": [
        {
          "filename": "templates/index.json"
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### Create or update theme files in bulk

  #### Query

  ```graphql
  mutation themeFilesUpsert($files: [OnlineStoreThemeFilesUpsertFileInput!]!, $themeId: ID!) {
    themeFilesUpsert(files: $files, themeId: $themeId) {
      upsertedThemeFiles {
        filename
      }
      job {
        id
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
        "filename": "templates/index.json",
        "body": {
          "type": "TEXT",
          "value": "{ \"sections\": {}, \"order\": [] }"
        }
      },
      {
        "filename": "assets/custom-content.txt",
        "body": {
          "type": "BASE64",
          "value": "Y3VzdG9tIGNvbnRlbnQ="
        }
      },
      {
        "filename": "assets/large-dog-image.jpg",
        "body": {
          "type": "URL",
          "value": "https://www.example.com/large-dog-image.jpg"
        }
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
  "query": "mutation themeFilesUpsert($files: [OnlineStoreThemeFilesUpsertFileInput!]!, $themeId: ID!) { themeFilesUpsert(files: $files, themeId: $themeId) { upsertedThemeFiles { filename } job { id } userErrors { field message } } }",
   "variables": {
      "themeId": "gid://shopify/OnlineStoreTheme/529529152",
      "files": [
        {
          "filename": "templates/index.json",
          "body": {
            "type": "TEXT",
            "value": "{ \"sections\": {}, \"order\": [] }"
          }
        },
        {
          "filename": "assets/custom-content.txt",
          "body": {
            "type": "BASE64",
            "value": "Y3VzdG9tIGNvbnRlbnQ="
          }
        },
        {
          "filename": "assets/large-dog-image.jpg",
          "body": {
            "type": "URL",
            "value": "https://www.example.com/large-dog-image.jpg"
          }
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
    mutation themeFilesUpsert($files: [OnlineStoreThemeFilesUpsertFileInput!]!, $themeId: ID!) {
      themeFilesUpsert(files: $files, themeId: $themeId) {
        upsertedThemeFiles {
          filename
        }
        job {
          id
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
                  "filename": "templates/index.json",
                  "body": {
                      "type": "TEXT",
                      "value": "{ \"sections\": {}, \"order\": [] }"
                  }
              },
              {
                  "filename": "assets/custom-content.txt",
                  "body": {
                      "type": "BASE64",
                      "value": "Y3VzdG9tIGNvbnRlbnQ="
                  }
              },
              {
                  "filename": "assets/large-dog-image.jpg",
                  "body": {
                      "type": "URL",
                      "value": "https://www.example.com/large-dog-image.jpg"
                  }
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
    mutation themeFilesUpsert($files: [OnlineStoreThemeFilesUpsertFileInput!]!, $themeId: ID!) {
      themeFilesUpsert(files: $files, themeId: $themeId) {
        upsertedThemeFiles {
          filename
        }
        job {
          id
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
        "filename": "templates/index.json",
        "body": {
          "type": "TEXT",
          "value": "{ \"sections\": {}, \"order\": [] }"
        }
      },
      {
        "filename": "assets/custom-content.txt",
        "body": {
          "type": "BASE64",
          "value": "Y3VzdG9tIGNvbnRlbnQ="
        }
      },
      {
        "filename": "assets/large-dog-image.jpg",
        "body": {
          "type": "URL",
          "value": "https://www.example.com/large-dog-image.jpg"
        }
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
      "query": `mutation themeFilesUpsert($files: [OnlineStoreThemeFilesUpsertFileInput!]!, $themeId: ID!) {
        themeFilesUpsert(files: $files, themeId: $themeId) {
          upsertedThemeFiles {
            filename
          }
          job {
            id
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
                  "filename": "templates/index.json",
                  "body": {
                      "type": "TEXT",
                      "value": "{ \"sections\": {}, \"order\": [] }"
                  }
              },
              {
                  "filename": "assets/custom-content.txt",
                  "body": {
                      "type": "BASE64",
                      "value": "Y3VzdG9tIGNvbnRlbnQ="
                  }
              },
              {
                  "filename": "assets/large-dog-image.jpg",
                  "body": {
                      "type": "URL",
                      "value": "https://www.example.com/large-dog-image.jpg"
                  }
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
  'mutation themeFilesUpsert($files: [OnlineStoreThemeFilesUpsertFileInput!]!, $themeId: ID!) {
    themeFilesUpsert(files: $files, themeId: $themeId) {
      upsertedThemeFiles {
        filename
      }
      job {
        id
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
        "filename": "templates/index.json",
        "body": {
          "type": "TEXT",
          "value": "{ \"sections\": {}, \"order\": [] }"
        }
      },
      {
        "filename": "assets/custom-content.txt",
        "body": {
          "type": "BASE64",
          "value": "Y3VzdG9tIGNvbnRlbnQ="
        }
      },
      {
        "filename": "assets/large-dog-image.jpg",
        "body": {
          "type": "URL",
          "value": "https://www.example.com/large-dog-image.jpg"
        }
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "themeFilesUpsert": {
      "upsertedThemeFiles": [
        {
          "filename": "templates/index.json"
        },
        {
          "filename": "assets/custom-content.txt"
        }
      ],
      "job": {
        "id": "gid://shopify/Job/ae8d210d-90e0-4912-96d0-96d45c5e8fbb"
      },
      "userErrors": []
    }
  }
  ```

* ### themeFilesUpsert reference
