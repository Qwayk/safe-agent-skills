---
title: articleDelete - GraphQL Admin
description: >-
  Permanently deletes a blog article from a shop's blog. This mutation removes
  the article and all associated metadata.


  For example, when outdated product information or seasonal content needs
  removal, merchants can use this mutation to clean up their blog.


  Use the `articleDelete` mutation to:

  - Remove outdated or incorrect blog content

  - Clean up seasonal or time-sensitive articles

  - Maintain blog organization


  The deletion is permanent and returns the deleted article's ID for
  confirmation.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/articleDelete'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/articleDelete.md'
---

# article​Delete

mutation

Requires Any of `write_content`, `write_online_store_pages` access scopes.

Permanently deletes a blog article from a shop's blog. This mutation removes the article and all associated metadata.

For example, when outdated product information or seasonal content needs removal, merchants can use this mutation to clean up their blog.

Use the `articleDelete` mutation to:

* Remove outdated or incorrect blog content
* Clean up seasonal or time-sensitive articles
* Maintain blog organization

The deletion is permanent and returns the deleted article's ID for confirmation.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the article to be deleted.

***

## Article​Delete​Payload returns

* deleted​Article​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the deleted article.

* user​Errors

  [\[Article​Delete​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ArticleDeleteUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Deletes an article

  #### Query

  ```graphql
  mutation DeleteArticle($id: ID!) {
    articleDelete(id: $id) {
      deletedArticleId
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
    "id": "gid://shopify/Article/959752435"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation DeleteArticle($id: ID!) { articleDelete(id: $id) { deletedArticleId userErrors { code field message } } }",
   "variables": {
      "id": "gid://shopify/Article/959752435"
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
    mutation DeleteArticle($id: ID!) {
      articleDelete(id: $id) {
        deletedArticleId
        userErrors {
          code
          field
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/Article/959752435"
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
    mutation DeleteArticle($id: ID!) {
      articleDelete(id: $id) {
        deletedArticleId
        userErrors {
          code
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/Article/959752435"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation DeleteArticle($id: ID!) {
        articleDelete(id: $id) {
          deletedArticleId
          userErrors {
            code
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Article/959752435"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation DeleteArticle($id: ID!) {
    articleDelete(id: $id) {
      deletedArticleId
      userErrors {
        code
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/Article/959752435"
  }'
  ```

  #### Response

  ```json
  {
    "articleDelete": {
      "deletedArticleId": "gid://shopify/Article/959752435",
      "userErrors": []
    }
  }
  ```

* ### articleDelete reference
