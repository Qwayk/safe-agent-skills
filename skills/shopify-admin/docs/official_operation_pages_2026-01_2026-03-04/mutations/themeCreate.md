---
title: themeCreate - GraphQL Admin
description: >-
  Creates a theme from an external URL or staged upload. The theme source can
  either be a ZIP file hosted at a public URL or files previously uploaded using
  the
  [`stagedUploadsCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/stageduploadscreate)
  mutation. The theme displays in the [Themes
  page](https://admin.shopify.com/themes) in the Shopify admin.


  New themes have an
  [`UNPUBLISHED`](https://shopify.dev//docs/api/admin-graphql/latest/mutations/themeCreate#arguments-role.enums.UNPUBLISHED)
  role by default. You can optionally specify a
  [`DEVELOPMENT`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/themeCreate#arguments-role.enums.DEVELOPMENT)
  role for temporary themes used during development.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/themeCreate'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/themeCreate.md'
---

# theme​Create

mutation

Requires The user needs write\_themes and an exemption from Shopify to modify themes. If you think that your app is eligible for an exemption and should have access to this API, then you can [submit an exception request](https://docs.google.com/forms/d/e/1FAIpQLSfZTB1vxFC5d1-GPdqYunWRGUoDcOheHQzfK2RoEFEHrknt5g/viewform).

Creates a theme from an external URL or staged upload. The theme source can either be a ZIP file hosted at a public URL or files previously uploaded using the [`stagedUploadsCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/stageduploadscreate) mutation. The theme displays in the [Themes page](https://admin.shopify.com/themes) in the Shopify admin.

New themes have an [`UNPUBLISHED`](https://shopify.dev//docs/api/admin-graphql/latest/mutations/themeCreate#arguments-role.enums.UNPUBLISHED) role by default. You can optionally specify a [`DEVELOPMENT`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/themeCreate#arguments-role.enums.DEVELOPMENT) role for temporary themes used during development.

## Arguments

* name

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The name of the theme to be created.

* role

  [Theme​Role](https://shopify.dev/docs/api/admin-graphql/latest/enums/ThemeRole)

  Default:UNPUBLISHED

  The role of the theme to be created. Only UNPUBLISHED and DEVELOPMENT roles are permitted.

* source

  [URL!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

  required

  An external URL or a [staged upload URL](https://shopify.dev/api/admin-graphql/latest/mutations/stageduploadscreate) of the theme to import.

***

## Theme​Create​Payload returns

* theme

  [Online​Store​Theme](https://shopify.dev/docs/api/admin-graphql/latest/objects/OnlineStoreTheme)

  The theme that was created.

* user​Errors

  [\[Theme​Create​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ThemeCreateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a new theme from an url with a custom name

  #### Query

  ```graphql
  mutation themeCreate($source: URL!, $name: String!) {
    themeCreate(source: $source, name: $name) {
      theme {
        name
        role
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
    "source": "http://www.example.com/dawn.zip",
    "name": "Dawn"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation themeCreate($source: URL!, $name: String!) { themeCreate(source: $source, name: $name) { theme { name role } userErrors { field message } } }",
   "variables": {
      "source": "http://www.example.com/dawn.zip",
      "name": "Dawn"
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
    mutation themeCreate($source: URL!, $name: String!) {
      themeCreate(source: $source, name: $name) {
        theme {
          name
          role
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "source": "http://www.example.com/dawn.zip",
          "name": "Dawn"
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
    mutation themeCreate($source: URL!, $name: String!) {
      themeCreate(source: $source, name: $name) {
        theme {
          name
          role
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "source": "http://www.example.com/dawn.zip",
    "name": "Dawn"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation themeCreate($source: URL!, $name: String!) {
        themeCreate(source: $source, name: $name) {
          theme {
            name
            role
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "source": "http://www.example.com/dawn.zip",
          "name": "Dawn"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation themeCreate($source: URL!, $name: String!) {
    themeCreate(source: $source, name: $name) {
      theme {
        name
        role
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "source": "http://www.example.com/dawn.zip",
    "name": "Dawn"
  }'
  ```

  #### Response

  ```json
  {
    "themeCreate": {
      "theme": {
        "name": "Dawn",
        "role": "UNPUBLISHED"
      },
      "userErrors": []
    }
  }
  ```

* ### Creates a theme

  #### Query

  ```graphql
  mutation ThemeCreate($name: String, $source: URL!) {
    themeCreate(name: $name, source: $source) {
      theme {
        id
      }
      userErrors {
        code
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "name": "New Theme",
    "source": "http://someurl.com/lemongrass.zip"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation ThemeCreate($name: String, $source: URL!) { themeCreate(name: $name, source: $source) { theme { id } userErrors { code field message } } }",
   "variables": {
      "name": "New Theme",
      "source": "http://someurl.com/lemongrass.zip"
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
    mutation ThemeCreate($name: String, $source: URL!) {
      themeCreate(name: $name, source: $source) {
        theme {
          id
        }
        userErrors {
          code
          field
          message
        }
      }
    }`,
    {
      variables: {
          "name": "New Theme",
          "source": "http://someurl.com/lemongrass.zip"
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
    mutation ThemeCreate($name: String, $source: URL!) {
      themeCreate(name: $name, source: $source) {
        theme {
          id
        }
        userErrors {
          code
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "name": "New Theme",
    "source": "http://someurl.com/lemongrass.zip"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation ThemeCreate($name: String, $source: URL!) {
        themeCreate(name: $name, source: $source) {
          theme {
            id
          }
          userErrors {
            code
            field
            message
          }
        }
      }`,
      "variables": {
          "name": "New Theme",
          "source": "http://someurl.com/lemongrass.zip"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation ThemeCreate($name: String, $source: URL!) {
    themeCreate(name: $name, source: $source) {
      theme {
        id
      }
      userErrors {
        code
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "name": "New Theme",
    "source": "http://someurl.com/lemongrass.zip"
  }'
  ```

  #### Response

  ```json
  {
    "themeCreate": {
      "theme": {
        "id": "gid://shopify/OnlineStoreTheme/1049083724"
      },
      "userErrors": []
    }
  }
  ```

* ### themeCreate reference
