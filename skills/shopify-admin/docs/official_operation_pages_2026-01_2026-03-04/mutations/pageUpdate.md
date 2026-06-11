---
title: pageUpdate - GraphQL Admin
description: >-
  Updates an existing page's content and settings.


  For example, merchants can update their "Shipping Policy" page when rates
  change, or refresh their "About Us" page with new team information.


  Use the `pageUpdate` mutation to:

  - Update page content and titles

  - Modify publication status

  - Change page handles for URL structure

  - Adjust template settings


  The mutation supports partial updates, allowing specific changes while
  preserving other page properties.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/pageUpdate'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/pageUpdate.md'
---

# page​Update

mutation

Requires Any of `write_content`, `write_online_store_pages` access scopes.

Updates an existing page's content and settings.

For example, merchants can update their "Shipping Policy" page when rates change, or refresh their "About Us" page with new team information.

Use the `pageUpdate` mutation to:

* Update page content and titles
* Modify publication status
* Change page handles for URL structure
* Adjust template settings

The mutation supports partial updates, allowing specific changes while preserving other page properties.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the page to be updated.

* page

  [Page​Update​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/PageUpdateInput)

  required

  The properties of the page to be updated.

***

## Page​Update​Payload returns

* page

  [Page](https://shopify.dev/docs/api/admin-graphql/latest/objects/Page)

  The page that was updated.

* user​Errors

  [\[Page​Update​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageUpdateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Updates a page

  #### Query

  ```graphql
  mutation UpdatePage($id: ID!, $page: PageUpdateInput!) {
    pageUpdate(id: $id, page: $page) {
      page {
        id
        title
        handle
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
    "id": "gid://shopify/Page/602767277",
    "page": {
      "title": "This is the Title",
      "handle": "this-is-the-handle"
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
  "query": "mutation UpdatePage($id: ID!, $page: PageUpdateInput!) { pageUpdate(id: $id, page: $page) { page { id title handle } userErrors { code field message } } }",
   "variables": {
      "id": "gid://shopify/Page/602767277",
      "page": {
        "title": "This is the Title",
        "handle": "this-is-the-handle"
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
    mutation UpdatePage($id: ID!, $page: PageUpdateInput!) {
      pageUpdate(id: $id, page: $page) {
        page {
          id
          title
          handle
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
          "id": "gid://shopify/Page/602767277",
          "page": {
              "title": "This is the Title",
              "handle": "this-is-the-handle"
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
    mutation UpdatePage($id: ID!, $page: PageUpdateInput!) {
      pageUpdate(id: $id, page: $page) {
        page {
          id
          title
          handle
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
    "id": "gid://shopify/Page/602767277",
    "page": {
      "title": "This is the Title",
      "handle": "this-is-the-handle"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation UpdatePage($id: ID!, $page: PageUpdateInput!) {
        pageUpdate(id: $id, page: $page) {
          page {
            id
            title
            handle
          }
          userErrors {
            code
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Page/602767277",
          "page": {
              "title": "This is the Title",
              "handle": "this-is-the-handle"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation UpdatePage($id: ID!, $page: PageUpdateInput!) {
    pageUpdate(id: $id, page: $page) {
      page {
        id
        title
        handle
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
    "id": "gid://shopify/Page/602767277",
    "page": {
      "title": "This is the Title",
      "handle": "this-is-the-handle"
    }
  }'
  ```

  #### Response

  ```json
  {
    "pageUpdate": {
      "page": {
        "id": "gid://shopify/Page/602767277",
        "title": "This is the Title",
        "handle": "this-is-the-handle"
      },
      "userErrors": []
    }
  }
  ```

* ### pageUpdate reference
