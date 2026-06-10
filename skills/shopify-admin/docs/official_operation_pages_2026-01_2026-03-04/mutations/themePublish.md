---
title: themePublish - GraphQL Admin
description: Publishes a theme.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/themePublish'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/themePublish.md'
---

# theme​Publish

mutation

Requires The user needs write\_themes and an exemption from Shopify to modify themes. If you think that your app is eligible for an exemption and should have access to this API, then you can [submit an exception request](https://docs.google.com/forms/d/e/1FAIpQLSfZTB1vxFC5d1-GPdqYunWRGUoDcOheHQzfK2RoEFEHrknt5g/viewform).

Publishes a theme.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  ID of the theme to be published.

***

## Theme​Publish​Payload returns

* theme

  [Online​Store​Theme](https://shopify.dev/docs/api/admin-graphql/latest/objects/OnlineStoreTheme)

  The theme that was published.

* user​Errors

  [\[Theme​Publish​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ThemePublishUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Modify an existing Theme

  #### Query

  ```graphql
  mutation themePublish($id: ID!) {
    themePublish(id: $id) {
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
    "id": "gid://shopify/OnlineStoreTheme/908009861"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation themePublish($id: ID!) { themePublish(id: $id) { theme { id } userErrors { code field message } } }",
   "variables": {
      "id": "gid://shopify/OnlineStoreTheme/908009861"
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
    mutation themePublish($id: ID!) {
      themePublish(id: $id) {
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
          "id": "gid://shopify/OnlineStoreTheme/908009861"
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
    mutation themePublish($id: ID!) {
      themePublish(id: $id) {
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
    "id": "gid://shopify/OnlineStoreTheme/908009861"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation themePublish($id: ID!) {
        themePublish(id: $id) {
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
          "id": "gid://shopify/OnlineStoreTheme/908009861"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation themePublish($id: ID!) {
    themePublish(id: $id) {
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
    "id": "gid://shopify/OnlineStoreTheme/908009861"
  }'
  ```

  #### Response

  ```json
  {
    "themePublish": {
      "theme": {
        "id": "gid://shopify/OnlineStoreTheme/908009861"
      },
      "userErrors": []
    }
  }
  ```

* ### Publish a theme

  #### Query

  ```graphql
  mutation themePublish($id: ID!) {
    themePublish(id: $id) {
      theme {
        id
        name
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
    "id": "gid://shopify/OnlineStoreTheme/908009861"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation themePublish($id: ID!) { themePublish(id: $id) { theme { id name } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/OnlineStoreTheme/908009861"
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
    mutation themePublish($id: ID!) {
      themePublish(id: $id) {
        theme {
          id
          name
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/OnlineStoreTheme/908009861"
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
    mutation themePublish($id: ID!) {
      themePublish(id: $id) {
        theme {
          id
          name
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/OnlineStoreTheme/908009861"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation themePublish($id: ID!) {
        themePublish(id: $id) {
          theme {
            id
            name
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/OnlineStoreTheme/908009861"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation themePublish($id: ID!) {
    themePublish(id: $id) {
      theme {
        id
        name
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/OnlineStoreTheme/908009861"
  }'
  ```

  #### Response

  ```json
  {
    "themePublish": {
      "theme": {
        "id": "gid://shopify/OnlineStoreTheme/908009861",
        "name": "Sandbox"
      },
      "userErrors": []
    }
  }
  ```

* ### themePublish reference
