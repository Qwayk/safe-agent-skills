---
title: pageDelete - GraphQL Admin
description: >-
  Permanently deletes a page from the online store.


  For example, merchants might delete seasonal landing pages after campaigns
  end, or remove outdated policy pages when terms change.


  Use the `pageDelete` mutation to:

  - Remove outdated or unnecessary pages

  - Clean up seasonal landing pages

  - Delete duplicate pages


  The deletion is permanent and returns the deleted page's ID for confirmation.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/pageDelete'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/pageDelete.md'
---

# page​Delete

mutation

Requires Any of `write_content`, `write_online_store_pages` access scopes.

Permanently deletes a page from the online store.

For example, merchants might delete seasonal landing pages after campaigns end, or remove outdated policy pages when terms change.

Use the `pageDelete` mutation to:

* Remove outdated or unnecessary pages
* Clean up seasonal landing pages
* Delete duplicate pages

The deletion is permanent and returns the deleted page's ID for confirmation.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the page to be deleted.

***

## Page​Delete​Payload returns

* deleted​Page​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the deleted page.

* user​Errors

  [\[Page​Delete​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageDeleteUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Deletes a page

  #### Query

  ```graphql
  mutation DeletePage($id: ID!) {
    pageDelete(id: $id) {
      deletedPageId
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
    "id": "gid://shopify/Page/602767277"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation DeletePage($id: ID!) { pageDelete(id: $id) { deletedPageId userErrors { code field message } } }",
   "variables": {
      "id": "gid://shopify/Page/602767277"
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
    mutation DeletePage($id: ID!) {
      pageDelete(id: $id) {
        deletedPageId
        userErrors {
          code
          field
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/Page/602767277"
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
    mutation DeletePage($id: ID!) {
      pageDelete(id: $id) {
        deletedPageId
        userErrors {
          code
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/Page/602767277"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation DeletePage($id: ID!) {
        pageDelete(id: $id) {
          deletedPageId
          userErrors {
            code
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Page/602767277"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation DeletePage($id: ID!) {
    pageDelete(id: $id) {
      deletedPageId
      userErrors {
        code
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/Page/602767277"
  }'
  ```

  #### Response

  ```json
  {
    "pageDelete": {
      "deletedPageId": "gid://shopify/Page/602767277",
      "userErrors": []
    }
  }
  ```

* ### pageDelete reference
