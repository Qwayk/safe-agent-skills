---
title: blogCreate - GraphQL Admin
description: >-
  Creates a new blog within a shop, establishing a container for organizing
  articles.


  For example, a fitness equipment retailer launching a wellness blog would use
  this mutation to create the blog, enabling them to publish workout guides and
  nutrition tips.


  Use the `blogCreate` mutation to:

  - Launch new content marketing initiatives

  - Create separate blogs for different content themes

  - Establish spaces for article organization


  The mutation validates blog settings and establishes the structure for article
  publishing.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/blogCreate'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/blogCreate.md'
---

# blog​Create

mutation

Requires Any of `write_content`, `write_online_store_pages` access scopes.

Creates a new blog within a shop, establishing a container for organizing articles.

For example, a fitness equipment retailer launching a wellness blog would use this mutation to create the blog, enabling them to publish workout guides and nutrition tips.

Use the `blogCreate` mutation to:

* Launch new content marketing initiatives
* Create separate blogs for different content themes
* Establish spaces for article organization

The mutation validates blog settings and establishes the structure for article publishing.

## Arguments

* blog

  [Blog​Create​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/BlogCreateInput)

  required

  The properties of the new blog.

***

## Blog​Create​Payload returns

* blog

  [Blog](https://shopify.dev/docs/api/admin-graphql/latest/objects/Blog)

  The blog that was created.

* user​Errors

  [\[Blog​Create​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/BlogCreateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a new Blog

  #### Description

  Creating a blog with all required fields and proper permissions results in a successful creation and returns the new blog details.

  #### Query

  ```graphql
  mutation CreateBlog($blog: BlogCreateInput!) {
    blogCreate(blog: $blog) {
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
    "blog": {
      "title": "New Blog Title",
      "handle": "new-blog-title",
      "templateSuffix": "standard",
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
  "query": "mutation CreateBlog($blog: BlogCreateInput!) { blogCreate(blog: $blog) { blog { id title handle templateSuffix commentPolicy } userErrors { code field message } } }",
   "variables": {
      "blog": {
        "title": "New Blog Title",
        "handle": "new-blog-title",
        "templateSuffix": "standard",
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
    mutation CreateBlog($blog: BlogCreateInput!) {
      blogCreate(blog: $blog) {
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
          "blog": {
              "title": "New Blog Title",
              "handle": "new-blog-title",
              "templateSuffix": "standard",
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
    mutation CreateBlog($blog: BlogCreateInput!) {
      blogCreate(blog: $blog) {
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
    "blog": {
      "title": "New Blog Title",
      "handle": "new-blog-title",
      "templateSuffix": "standard",
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
      "query": `mutation CreateBlog($blog: BlogCreateInput!) {
        blogCreate(blog: $blog) {
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
          "blog": {
              "title": "New Blog Title",
              "handle": "new-blog-title",
              "templateSuffix": "standard",
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
  'mutation CreateBlog($blog: BlogCreateInput!) {
    blogCreate(blog: $blog) {
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
    "blog": {
      "title": "New Blog Title",
      "handle": "new-blog-title",
      "templateSuffix": "standard",
      "commentPolicy": "MODERATED"
    }
  }'
  ```

  #### Response

  ```json
  {
    "blogCreate": {
      "blog": {
        "id": "gid://shopify/Blog/1008414248",
        "title": "New Blog Title",
        "handle": "new-blog-title",
        "templateSuffix": "standard",
        "commentPolicy": "MODERATED"
      },
      "userErrors": []
    }
  }
  ```

* ### blogCreate reference
