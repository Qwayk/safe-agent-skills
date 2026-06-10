---
title: blogUpdate - GraphQL Admin
description: >-
  Updates an existing blog's configuration and settings. This mutation allows
  merchants to modify blog properties to keep their content strategy current.


  For example, a merchant might update their blog's title from "Company News" to
  "Sustainability Stories" when shifting their content focus, or modify the
  handle to improve URL structure.


  Use the `blogUpdate` mutation to:

  - Change blog titles for rebranding

  - Modify blog handles for better URLs

  - Adjust comment settings and moderation preferences


  The mutation returns the updated blog with any validation errors.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/blogUpdate'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/blogUpdate.md'
---

# blog​Update

mutation

Requires Any of `write_content`, `write_online_store_pages` access scopes.

Updates an existing blog's configuration and settings. This mutation allows merchants to modify blog properties to keep their content strategy current.

For example, a merchant might update their blog's title from "Company News" to "Sustainability Stories" when shifting their content focus, or modify the handle to improve URL structure.

Use the `blogUpdate` mutation to:

* Change blog titles for rebranding
* Modify blog handles for better URLs
* Adjust comment settings and moderation preferences

The mutation returns the updated blog with any validation errors.

## Arguments

* blog

  [Blog​Update​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/BlogUpdateInput)

  required

  The properties of the blog to be updated.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the blog to be updated.

***

## Blog​Update​Payload returns

* blog

  [Blog](https://shopify.dev/docs/api/admin-graphql/latest/objects/Blog)

  The blog that was updated.

* user​Errors

  [\[Blog​Update​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/BlogUpdateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Modify an existing Blog

  #### Query

  ```graphql
  mutation UpdateBlog($id: ID!, $blog: BlogUpdateInput!) {
    blogUpdate(id: $id, blog: $blog) {
      blog {
        id
        title
        handle
        templateSuffix
        commentPolicy
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
    "id": "gid://shopify/Blog/389767568",
    "blog": {
      "title": "Updated Blog Title",
      "handle": "updated-blog-title",
      "templateSuffix": "updated_template",
      "commentPolicy": "MODERATED"
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
  "query": "mutation UpdateBlog($id: ID!, $blog: BlogUpdateInput!) { blogUpdate(id: $id, blog: $blog) { blog { id title handle templateSuffix commentPolicy } userErrors { code field message } } }",
   "variables": {
      "id": "gid://shopify/Blog/389767568",
      "blog": {
        "title": "Updated Blog Title",
        "handle": "updated-blog-title",
        "templateSuffix": "updated_template",
        "commentPolicy": "MODERATED"
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
    mutation UpdateBlog($id: ID!, $blog: BlogUpdateInput!) {
      blogUpdate(id: $id, blog: $blog) {
        blog {
          id
          title
          handle
          templateSuffix
          commentPolicy
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
          "id": "gid://shopify/Blog/389767568",
          "blog": {
              "title": "Updated Blog Title",
              "handle": "updated-blog-title",
              "templateSuffix": "updated_template",
              "commentPolicy": "MODERATED"
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
    mutation UpdateBlog($id: ID!, $blog: BlogUpdateInput!) {
      blogUpdate(id: $id, blog: $blog) {
        blog {
          id
          title
          handle
          templateSuffix
          commentPolicy
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
    "id": "gid://shopify/Blog/389767568",
    "blog": {
      "title": "Updated Blog Title",
      "handle": "updated-blog-title",
      "templateSuffix": "updated_template",
      "commentPolicy": "MODERATED"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation UpdateBlog($id: ID!, $blog: BlogUpdateInput!) {
        blogUpdate(id: $id, blog: $blog) {
          blog {
            id
            title
            handle
            templateSuffix
            commentPolicy
          }
          userErrors {
            code
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Blog/389767568",
          "blog": {
              "title": "Updated Blog Title",
              "handle": "updated-blog-title",
              "templateSuffix": "updated_template",
              "commentPolicy": "MODERATED"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation UpdateBlog($id: ID!, $blog: BlogUpdateInput!) {
    blogUpdate(id: $id, blog: $blog) {
      blog {
        id
        title
        handle
        templateSuffix
        commentPolicy
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
    "id": "gid://shopify/Blog/389767568",
    "blog": {
      "title": "Updated Blog Title",
      "handle": "updated-blog-title",
      "templateSuffix": "updated_template",
      "commentPolicy": "MODERATED"
    }
  }'
  ```

  #### Response

  ```json
  {
    "blogUpdate": {
      "blog": {
        "id": "gid://shopify/Blog/389767568",
        "title": "Updated Blog Title",
        "handle": "updated-blog-title",
        "templateSuffix": "updated_template",
        "commentPolicy": "MODERATED"
      },
      "userErrors": []
    }
  }
  ```

* ### blogUpdate reference
