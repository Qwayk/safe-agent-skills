---
title: comments - GraphQL Admin
description: List of the shop's comments.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/comments'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/comments.md'
---

# comments

query

List of the shop's comments.

## CommentConnection arguments

[CommentConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/CommentConnection)

* after

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* before

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* first

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* last

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* query

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

  * * default

      string

    * created\_at

      time

    * id

      id

    * published\_at

      time

    * published\_status

      string

    * status

      string

    - Filter by a case-insensitive search of multiple fields in a document.

    - Example:

      * `query=Bob Norman`
      * `query=title:green hoodie`

      Filter by the date and time when the comment was created.

    - Example:

      * `created_at:>'2020-10-21T23:39:20Z'`
      * `created_at:<now`
      * `created_at:<=2024`

      Filter by `id` range.

    - Example:

      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

      Filter by the date and time when the comment was published.

    - Example:

      * `published_at:>'2020-10-21T23:39:20Z'`
      * `published_at:<now`
      * `published_at:<=2024`

      Filter by published status

    - Valid values:
      * `any`
      * `published`
      * `unpublished`
      Example:
      * `published_status:any`
      * `published_status:published`
      * `published_status:unpublished`

  * updated\_at

    time

    Filter by the date and time when the comment was last updated.

    Example:

    * `updated_at:>'2020-10-21T23:39:20Z'`
    * `updated_at:<now`
    * `updated_at:<=2024`

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* sort​Key

  [Comment​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/CommentSortKeys)

  Default:ID

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Comment​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CommentEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Comment!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Comment)

  non-null

  A list of nodes that are contained in CommentEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Retrieves a list of comments

  #### Query

  ```graphql
  query CommentList {
    comments(first: 50) {
      nodes {
        id
        body
        bodyHtml
        author {
          name
        }
        ip
        publishedAt
        status
        userAgent
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
  "query": "query CommentList { comments(first: 50) { nodes { id body bodyHtml author { name } ip publishedAt status userAgent } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query CommentList {
      comments(first: 50) {
        nodes {
          id
          body
          bodyHtml
          author {
            name
          }
          ip
          publishedAt
          status
          userAgent
        }
      }
    }`,
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
    query CommentList {
      comments(first: 50) {
        nodes {
          id
          body
          bodyHtml
          author {
            name
          }
          ip
          publishedAt
          status
          userAgent
        }
      }
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `query CommentList {
      comments(first: 50) {
        nodes {
          id
          body
          bodyHtml
          author {
            name
          }
          ip
          publishedAt
          status
          userAgent
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query CommentList {
    comments(first: 50) {
      nodes {
        id
        body
        bodyHtml
        author {
          name
        }
        ip
        publishedAt
        status
        userAgent
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "comments": {
      "nodes": [
        {
          "id": "gid://shopify/Comment/9450891",
          "body": "Check my casino at ... This will be marked as spam by akismet, because of the author name.",
          "bodyHtml": "<p>Check my casino at ... This will be marked as spam by akismet, because of the author name.</p>",
          "author": {
            "name": "viagra-test-123"
          },
          "ip": "127.0.0.1",
          "publishedAt": null,
          "status": "SPAM",
          "userAgent": "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_4; en-us) AppleWebKit/525.18 (KHTML, like Gecko) Version/3.1.2 Safari/525.20.1"
        },
        {
          "id": "gid://shopify/Comment/52127930",
          "body": "Hi author, I really _like_ what you're doing there.",
          "bodyHtml": "<p>Hi author, I really <em>like</em> what you're doing there.</p>",
          "author": {
            "name": "Soleone"
          },
          "ip": "127.0.0.1",
          "publishedAt": null,
          "status": "PENDING",
          "userAgent": "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_4; en-us) AppleWebKit/525.18 (KHTML, like Gecko) Version/3.1.2 Safari/525.20.1"
        },
        {
          "id": "gid://shopify/Comment/64683838",
          "body": "Check my casino at ... This will be marked as spam by akismet, because of the author name.",
          "bodyHtml": "<p>Check my casino at ... This will be marked as spam by akismet, because of the author name.</p>",
          "author": {
            "name": "viagra-test-123"
          },
          "ip": "127.0.0.1",
          "publishedAt": null,
          "status": "PENDING",
          "userAgent": "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_4; en-us) AppleWebKit/525.18 (KHTML, like Gecko) Version/3.1.2 Safari/525.20.1"
        },
        {
          "id": "gid://shopify/Comment/145356500",
          "body": "Great blog, love it!",
          "bodyHtml": "<p>Great blog, love it!</p>",
          "author": {
            "name": "Bob Bobsen"
          },
          "ip": "127.0.0.1",
          "publishedAt": null,
          "status": "PUBLISHED",
          "userAgent": "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_4; en-us) AppleWebKit/525.18 (KHTML, like Gecko) Version/3.1.2 Safari/525.20.1"
        },
        {
          "id": "gid://shopify/Comment/757536350",
          "body": "Check my casino at ... This will be marked as spam by akismet, because of the author name.",
          "bodyHtml": "<p>Check my casino at ... This will be marked as spam by akismet, because of the author name.</p>",
          "author": {
            "name": "viagra-test-123"
          },
          "ip": "127.0.0.1",
          "publishedAt": null,
          "status": "UNAPPROVED",
          "userAgent": "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_4; en-us) AppleWebKit/525.18 (KHTML, like Gecko) Version/3.1.2 Safari/525.20.1"
        }
      ]
    }
  }
  ```
