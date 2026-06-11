---
title: pageCreate - GraphQL Admin
description: >-
  Creates a
  [`Page`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Page) for
  the online store.


  Pages contain custom content like "About Us" or "Contact" information that
  merchants display outside their product catalog. The page requires a
  [`title`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Page#field-Page.fields.title)
  and can include HTML content, publishing settings, and custom [template
  suffixes](https://shopify.dev/docs/api/admin-graphql/latest/objects/Page#field-Page.fields.templateSuffix).
  You can control visibility through the
  [`isPublished`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Page#field-Page.fields.isPublished)
  flag or schedule publication with a specific date.


  The mutation returns the complete page object upon successful creation or
  validation errors if the input is invalid.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/pageCreate'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/pageCreate.md'
---

# page​Create

mutation

Requires Any of `write_content`, `write_online_store_pages` access scopes.

Creates a [`Page`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Page) for the online store.

Pages contain custom content like "About Us" or "Contact" information that merchants display outside their product catalog. The page requires a [`title`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Page#field-Page.fields.title) and can include HTML content, publishing settings, and custom [template suffixes](https://shopify.dev/docs/api/admin-graphql/latest/objects/Page#field-Page.fields.templateSuffix). You can control visibility through the [`isPublished`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Page#field-Page.fields.isPublished) flag or schedule publication with a specific date.

The mutation returns the complete page object upon successful creation or validation errors if the input is invalid.

## Arguments

* page

  [Page​Create​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/PageCreateInput)

  required

  The properties of the new page.

***

## Page​Create​Payload returns

* page

  [Page](https://shopify.dev/docs/api/admin-graphql/latest/objects/Page)

  The page that was created.

* user​Errors

  [\[Page​Create​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageCreateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Creates a page

  #### Query

  ```graphql
  mutation CreatePage($page: PageCreateInput!) {
    pageCreate(page: $page) {
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
    "page": {
      "title": "New Page Title",
      "handle": "new-page-title",
      "body": "This is the content of the page.",
      "isPublished": true,
      "templateSuffix": "custom"
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
  "query": "mutation CreatePage($page: PageCreateInput!) { pageCreate(page: $page) { page { id title handle } userErrors { code field message } } }",
   "variables": {
      "page": {
        "title": "New Page Title",
        "handle": "new-page-title",
        "body": "This is the content of the page.",
        "isPublished": true,
        "templateSuffix": "custom"
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
    mutation CreatePage($page: PageCreateInput!) {
      pageCreate(page: $page) {
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
          "page": {
              "title": "New Page Title",
              "handle": "new-page-title",
              "body": "This is the content of the page.",
              "isPublished": true,
              "templateSuffix": "custom"
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
    mutation CreatePage($page: PageCreateInput!) {
      pageCreate(page: $page) {
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
    "page": {
      "title": "New Page Title",
      "handle": "new-page-title",
      "body": "This is the content of the page.",
      "isPublished": true,
      "templateSuffix": "custom"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation CreatePage($page: PageCreateInput!) {
        pageCreate(page: $page) {
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
          "page": {
              "title": "New Page Title",
              "handle": "new-page-title",
              "body": "This is the content of the page.",
              "isPublished": true,
              "templateSuffix": "custom"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation CreatePage($page: PageCreateInput!) {
    pageCreate(page: $page) {
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
    "page": {
      "title": "New Page Title",
      "handle": "new-page-title",
      "body": "This is the content of the page.",
      "isPublished": true,
      "templateSuffix": "custom"
    }
  }'
  ```

  #### Response

  ```json
  {
    "pageCreate": {
      "page": {
        "id": "gid://shopify/Page/1025371368",
        "title": "New Page Title",
        "handle": "new-page-title"
      },
      "userErrors": []
    }
  }
  ```

* ### pageCreate reference
