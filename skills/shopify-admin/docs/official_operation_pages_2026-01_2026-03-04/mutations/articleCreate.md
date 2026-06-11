---
title: articleCreate - GraphQL Admin
description: >-
  Creates an
  [`Article`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Article).
  Articles are content pieces that include a title, body text, and author
  information.


  You can publish the article immediately or schedule it with a specific publish
  date. You can customize the article's URL handle, apply custom templates for
  rendering, and add optional fields like
  [tags](https://shopify.dev/docs/api/admin-graphql/latest/mutations/articleCreate#arguments-article.fields.tags),
  an
  [image](https://shopify.dev/docs/api/admin-graphql/latest/mutations/articleCreate#arguments-article.fields.image),
  and
  [`Metafield`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Metafield)
  objects.


  The mutation validates article content and ensures proper blog association.
  Error handling provides specific feedback for content requirements.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/articleCreate'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/articleCreate.md'
---

# article​Create

mutation

Requires Any of `write_content`, `write_online_store_pages` access scopes.

Creates an [`Article`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Article). Articles are content pieces that include a title, body text, and author information.

You can publish the article immediately or schedule it with a specific publish date. You can customize the article's URL handle, apply custom templates for rendering, and add optional fields like [tags](https://shopify.dev/docs/api/admin-graphql/latest/mutations/articleCreate#arguments-article.fields.tags), an [image](https://shopify.dev/docs/api/admin-graphql/latest/mutations/articleCreate#arguments-article.fields.image), and [`Metafield`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Metafield) objects.

The mutation validates article content and ensures proper blog association. Error handling provides specific feedback for content requirements.

## Arguments

* article

  [Article​Create​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ArticleCreateInput)

  required

  The properties of the new article.

* blog

  [Article​Blog​Input](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ArticleBlogInput)

  The properties of the new blog.

***

## Article​Create​Payload returns

* article

  [Article](https://shopify.dev/docs/api/admin-graphql/latest/objects/Article)

  The article that was created.

* user​Errors

  [\[Article​Create​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ArticleCreateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Creates an article for a blog

  #### Query

  ```graphql
  mutation CreateArticle($article: ArticleCreateInput!) {
    articleCreate(article: $article) {
      article {
        id
        title
        author {
          name
        }
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
    "article": {
      "blogId": "gid://shopify/Blog/389767568",
      "title": "New Article Title",
      "author": {
        "name": "Test User"
      },
      "handle": "new-article-title",
      "body": "This is the content of the article.",
      "summary": "This is a summary of the article.",
      "isPublished": true,
      "publishDate": "2023-01-01T12:00:00Z",
      "tags": [
        "Tag1",
        "Tag2"
      ],
      "image": {
        "altText": "Alt text for the image",
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
  "query": "mutation CreateArticle($article: ArticleCreateInput!) { articleCreate(article: $article) { article { id title author { name } handle body summary tags image { altText originalSrc } } userErrors { code field message } } }",
   "variables": {
      "article": {
        "blogId": "gid://shopify/Blog/389767568",
        "title": "New Article Title",
        "author": {
          "name": "Test User"
        },
        "handle": "new-article-title",
        "body": "This is the content of the article.",
        "summary": "This is a summary of the article.",
        "isPublished": true,
        "publishDate": "2023-01-01T12:00:00Z",
        "tags": [
          "Tag1",
          "Tag2"
        ],
        "image": {
          "altText": "Alt text for the image",
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
    mutation CreateArticle($article: ArticleCreateInput!) {
      articleCreate(article: $article) {
        article {
          id
          title
          author {
            name
          }
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
          "article": {
              "blogId": "gid://shopify/Blog/389767568",
              "title": "New Article Title",
              "author": {
                  "name": "Test User"
              },
              "handle": "new-article-title",
              "body": "This is the content of the article.",
              "summary": "This is a summary of the article.",
              "isPublished": true,
              "publishDate": "2023-01-01T12:00:00Z",
              "tags": [
                  "Tag1",
                  "Tag2"
              ],
              "image": {
                  "altText": "Alt text for the image",
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
    mutation CreateArticle($article: ArticleCreateInput!) {
      articleCreate(article: $article) {
        article {
          id
          title
          author {
            name
          }
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
    "article": {
      "blogId": "gid://shopify/Blog/389767568",
      "title": "New Article Title",
      "author": {
        "name": "Test User"
      },
      "handle": "new-article-title",
      "body": "This is the content of the article.",
      "summary": "This is a summary of the article.",
      "isPublished": true,
      "publishDate": "2023-01-01T12:00:00Z",
      "tags": [
        "Tag1",
        "Tag2"
      ],
      "image": {
        "altText": "Alt text for the image",
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
      "query": `mutation CreateArticle($article: ArticleCreateInput!) {
        articleCreate(article: $article) {
          article {
            id
            title
            author {
              name
            }
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
          "article": {
              "blogId": "gid://shopify/Blog/389767568",
              "title": "New Article Title",
              "author": {
                  "name": "Test User"
              },
              "handle": "new-article-title",
              "body": "This is the content of the article.",
              "summary": "This is a summary of the article.",
              "isPublished": true,
              "publishDate": "2023-01-01T12:00:00Z",
              "tags": [
                  "Tag1",
                  "Tag2"
              ],
              "image": {
                  "altText": "Alt text for the image",
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
  'mutation CreateArticle($article: ArticleCreateInput!) {
    articleCreate(article: $article) {
      article {
        id
        title
        author {
          name
        }
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
    "article": {
      "blogId": "gid://shopify/Blog/389767568",
      "title": "New Article Title",
      "author": {
        "name": "Test User"
      },
      "handle": "new-article-title",
      "body": "This is the content of the article.",
      "summary": "This is a summary of the article.",
      "isPublished": true,
      "publishDate": "2023-01-01T12:00:00Z",
      "tags": [
        "Tag1",
        "Tag2"
      ],
      "image": {
        "altText": "Alt text for the image",
        "url": "http://example.com/fake_image.jpg"
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "articleCreate": {
      "article": {
        "id": "gid://shopify/Article/1051293784",
        "title": "New Article Title",
        "author": {
          "name": "Test User"
        },
        "handle": "new-article-title",
        "body": "This is the content of the article.",
        "summary": "This is a summary of the article.",
        "tags": [
          "Tag1",
          "Tag2"
        ],
        "image": {
          "altText": "Alt text for the image",
          "originalSrc": "https://cdn.shopify.com/s/files/1/2637/1970/articles/fake_image.jpg?v=1730243735"
        }
      },
      "userErrors": []
    }
  }
  ```

* ### articleCreate reference
