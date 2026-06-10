---
title: articleUpdate - GraphQL Admin
description: >-
  Updates an existing
  [`Article`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Article).
  You can modify the article's content, metadata, publication status, and
  associated properties like author information and tags.


  If you update the
  [`handle`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/articleUpdate#arguments-article.fields.handle),
  then you can optionally create a redirect from the old URL to the new one by
  setting
  [`redirectNewHandle`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/articleUpdate#arguments-article.fields.redirectNewHandle)
  to `true`.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/articleUpdate'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/articleUpdate.md'
---

# article​Update

mutation

Requires Any of `write_content`, `write_online_store_pages` access scopes.

Updates an existing [`Article`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Article). You can modify the article's content, metadata, publication status, and associated properties like author information and tags.

If you update the [`handle`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/articleUpdate#arguments-article.fields.handle), then you can optionally create a redirect from the old URL to the new one by setting [`redirectNewHandle`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/articleUpdate#arguments-article.fields.redirectNewHandle) to `true`.

## Arguments

* article

  [Article​Update​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ArticleUpdateInput)

  required

  The properties of the article to be updated.

* blog

  [Article​Blog​Input](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ArticleBlogInput)

  The properties of the blog to be created.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the article to be updated.

***

## Article​Update​Payload returns

* article

  [Article](https://shopify.dev/docs/api/admin-graphql/latest/objects/Article)

  The article that was updated.

* user​Errors

  [\[Article​Update​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ArticleUpdateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Updates an article

  #### Query

  ```graphql
  mutation UpdateArticle($id: ID!, $article: ArticleUpdateInput!) {
    articleUpdate(id: $id, article: $article) {
      article {
        id
        title
        handle
        body
        summary
        tags
        image {
          altText
          originalSrc
        }
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
    "id": "gid://shopify/Article/959752435",
    "article": {
      "title": "Updated Article Title",
      "handle": "updated-article-title",
      "body": "This is the updated content of the article.",
      "summary": "This is an updated summary of the article.",
      "tags": [
        "UpdatedTag1",
        "UpdatedTag2"
      ],
      "image": {
        "altText": "Updated alt text for the image",
        "url": "http://example.com/fake_image.jpg"
      }
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
  "query": "mutation UpdateArticle($id: ID!, $article: ArticleUpdateInput!) { articleUpdate(id: $id, article: $article) { article { id title handle body summary tags image { altText originalSrc } } userErrors { code field message } } }",
   "variables": {
      "id": "gid://shopify/Article/959752435",
      "article": {
        "title": "Updated Article Title",
        "handle": "updated-article-title",
        "body": "This is the updated content of the article.",
        "summary": "This is an updated summary of the article.",
        "tags": [
          "UpdatedTag1",
          "UpdatedTag2"
        ],
        "image": {
          "altText": "Updated alt text for the image",
          "url": "http://example.com/fake_image.jpg"
        }
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
    mutation UpdateArticle($id: ID!, $article: ArticleUpdateInput!) {
      articleUpdate(id: $id, article: $article) {
        article {
          id
          title
          handle
          body
          summary
          tags
          image {
            altText
            originalSrc
          }
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
          "id": "gid://shopify/Article/959752435",
          "article": {
              "title": "Updated Article Title",
              "handle": "updated-article-title",
              "body": "This is the updated content of the article.",
              "summary": "This is an updated summary of the article.",
              "tags": [
                  "UpdatedTag1",
                  "UpdatedTag2"
              ],
              "image": {
                  "altText": "Updated alt text for the image",
                  "url": "http://example.com/fake_image.jpg"
              }
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
    mutation UpdateArticle($id: ID!, $article: ArticleUpdateInput!) {
      articleUpdate(id: $id, article: $article) {
        article {
          id
          title
          handle
          body
          summary
          tags
          image {
            altText
            originalSrc
          }
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
    "id": "gid://shopify/Article/959752435",
    "article": {
      "title": "Updated Article Title",
      "handle": "updated-article-title",
      "body": "This is the updated content of the article.",
      "summary": "This is an updated summary of the article.",
      "tags": [
        "UpdatedTag1",
        "UpdatedTag2"
      ],
      "image": {
        "altText": "Updated alt text for the image",
        "url": "http://example.com/fake_image.jpg"
      }
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation UpdateArticle($id: ID!, $article: ArticleUpdateInput!) {
        articleUpdate(id: $id, article: $article) {
          article {
            id
            title
            handle
            body
            summary
            tags
            image {
              altText
              originalSrc
            }
          }
          userErrors {
            code
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Article/959752435",
          "article": {
              "title": "Updated Article Title",
              "handle": "updated-article-title",
              "body": "This is the updated content of the article.",
              "summary": "This is an updated summary of the article.",
              "tags": [
                  "UpdatedTag1",
                  "UpdatedTag2"
              ],
              "image": {
                  "altText": "Updated alt text for the image",
                  "url": "http://example.com/fake_image.jpg"
              }
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation UpdateArticle($id: ID!, $article: ArticleUpdateInput!) {
    articleUpdate(id: $id, article: $article) {
      article {
        id
        title
        handle
        body
        summary
        tags
        image {
          altText
          originalSrc
        }
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
    "id": "gid://shopify/Article/959752435",
    "article": {
      "title": "Updated Article Title",
      "handle": "updated-article-title",
      "body": "This is the updated content of the article.",
      "summary": "This is an updated summary of the article.",
      "tags": [
        "UpdatedTag1",
        "UpdatedTag2"
      ],
      "image": {
        "altText": "Updated alt text for the image",
        "url": "http://example.com/fake_image.jpg"
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "articleUpdate": {
      "article": {
        "id": "gid://shopify/Article/959752435",
        "title": "Updated Article Title",
        "handle": "updated-article-title",
        "body": "This is the updated content of the article.",
        "summary": "This is an updated summary of the article.",
        "tags": [
          "UpdatedTag1",
          "UpdatedTag2"
        ],
        "image": {
          "altText": "Updated alt text for the image",
          "originalSrc": "https://cdn.shopify.com/s/files/1/2637/1970/articles/fake_image.jpg?v=1730243702"
        }
      },
      "userErrors": []
    }
  }
  ```

* ### articleUpdate reference
