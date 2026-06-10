---
title: urlRedirectUpdate - GraphQL Admin
description: Updates a URL redirect.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/urlRedirectUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/urlRedirectUpdate.md
---

# url​Redirect​Update

mutation

Requires `write_online_store_navigation` access scope.

Updates a URL redirect.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the URL redirect to update.

* url​Redirect

  [Url​Redirect​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/UrlRedirectInput)

  required

  The input fields required to update the URL redirect.

***

## Url​Redirect​Update​Payload returns

* url​Redirect

  [Url​Redirect](https://shopify.dev/docs/api/admin-graphql/latest/objects/UrlRedirect)

  Returns the updated URL redirect.

* user​Errors

  [\[Url​Redirect​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UrlRedirectUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Updates an existing redirect

  #### Query

  ```graphql
  mutation UrlRedirectUpdate($id: ID!, $urlRedirect: UrlRedirectInput!) {
    urlRedirectUpdate(id: $id, urlRedirect: $urlRedirect) {
      urlRedirect {
        id
        path
        target
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
    "id": "gid://shopify/UrlRedirect/905192165",
    "urlRedirect": {
      "path": "/thepath",
      "target": "/thetarget"
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
  "query": "mutation UrlRedirectUpdate($id: ID!, $urlRedirect: UrlRedirectInput!) { urlRedirectUpdate(id: $id, urlRedirect: $urlRedirect) { urlRedirect { id path target } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/UrlRedirect/905192165",
      "urlRedirect": {
        "path": "/thepath",
        "target": "/thetarget"
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
    mutation UrlRedirectUpdate($id: ID!, $urlRedirect: UrlRedirectInput!) {
      urlRedirectUpdate(id: $id, urlRedirect: $urlRedirect) {
        urlRedirect {
          id
          path
          target
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/UrlRedirect/905192165",
          "urlRedirect": {
              "path": "/thepath",
              "target": "/thetarget"
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
    mutation UrlRedirectUpdate($id: ID!, $urlRedirect: UrlRedirectInput!) {
      urlRedirectUpdate(id: $id, urlRedirect: $urlRedirect) {
        urlRedirect {
          id
          path
          target
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/UrlRedirect/905192165",
    "urlRedirect": {
      "path": "/thepath",
      "target": "/thetarget"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation UrlRedirectUpdate($id: ID!, $urlRedirect: UrlRedirectInput!) {
        urlRedirectUpdate(id: $id, urlRedirect: $urlRedirect) {
          urlRedirect {
            id
            path
            target
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/UrlRedirect/905192165",
          "urlRedirect": {
              "path": "/thepath",
              "target": "/thetarget"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation UrlRedirectUpdate($id: ID!, $urlRedirect: UrlRedirectInput!) {
    urlRedirectUpdate(id: $id, urlRedirect: $urlRedirect) {
      urlRedirect {
        id
        path
        target
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/UrlRedirect/905192165",
    "urlRedirect": {
      "path": "/thepath",
      "target": "/thetarget"
    }
  }'
  ```

  #### Response

  ```json
  {
    "urlRedirectUpdate": {
      "urlRedirect": {
        "id": "gid://shopify/UrlRedirect/905192165",
        "path": "/thepath",
        "target": "/thetarget"
      },
      "userErrors": []
    }
  }
  ```

* ### urlRedirectUpdate reference
