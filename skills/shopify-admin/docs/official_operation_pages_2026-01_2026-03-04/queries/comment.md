---
title: comment - GraphQL Admin
description: Returns a `Comment` resource by ID.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/comment'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/comment.md'
---

# comment

query

Returns a `Comment` resource by ID.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the `Comment` to return.

***

## Possible returns

* Comment

  [Comment](https://shopify.dev/docs/api/admin-graphql/latest/objects/Comment)

  A comment on an article.

  * article

    [Article](https://shopify.dev/docs/api/admin-graphql/latest/objects/Article)

    The article associated with the comment.

  * author

    [Comment​Author!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CommentAuthor)

    non-null

    The comment’s author.

  * body

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The content of the comment.

  * body​Html

    [HTML!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/HTML)

    non-null

    The content of the comment, complete with HTML formatting.

  * created​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the comment was created.

  * events

    [Event​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/EventConnection)

    non-null

    The paginated list of events associated with the host subject.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * last

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * before

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * reverse

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Reverse the order of the underlying list.

    * sort​Key

      [Event​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/EventSortKeys)

      Default:ID

      Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

    * query

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

      * * action

          string

        * comments

          boolean

        * created\_at

          time

        * id

          id

        * subject\_type

          string

        - The action that occured.

        - Example:

          * `action:create`

          Whether or not to include [comment-events](https://shopify.dev/api/admin-graphql/latest/objects/CommentEvent) in your search, passing `false` will exclude comment-events, any other value will include comment-events.

        - Example:

          * `false`
          * `true`

          Filter by the date and time when the event occurred. Event data is retained for 1 year.

        - Example:

          * `created_at:>2025-10-21`
          * `created_at:<now`

          Filter by `id` range.

        - Example:

          * `id:1234`
          * `id:>=1234`
          * `id:<=1234`

          The resource type affected by this event. See [EventSubjectType](https://shopify.dev/api/admin-graphql/latest/enums/EventSubjectType) for possible values.

          Example:

          * `PRODUCT_VARIANT`
          * `PRODUCT`
          * `COLLECTION`

    ***

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * ip

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The IP address of the commenter.

  * is​Published

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether or not the comment is published.

  * published​At

    [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    The date and time when the comment was published.

  * status

    [Comment​Status!](https://shopify.dev/docs/api/admin-graphql/latest/enums/CommentStatus)

    non-null

    The status of the comment.

  * updated​At

    [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    The date and time when the comment was last updated.

  * user​Agent

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The user agent of the commenter.

***

## Examples

* ### Retrieves a single comment by its ID

  #### Query

  ```graphql
  query CommentShow($id: ID!) {
    comment(id: $id) {
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
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/Comment/9450891"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query CommentShow($id: ID!) { comment(id: $id) { id body bodyHtml author { name } ip publishedAt status userAgent } }",
   "variables": {
      "id": "gid://shopify/Comment/9450891"
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
    query CommentShow($id: ID!) {
      comment(id: $id) {
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
    }`,
    {
      variables: {
          "id": "gid://shopify/Comment/9450891"
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
    query CommentShow($id: ID!) {
      comment(id: $id) {
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
  QUERY

  variables = {
    "id": "gid://shopify/Comment/9450891"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query CommentShow($id: ID!) {
        comment(id: $id) {
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
      }`,
      "variables": {
          "id": "gid://shopify/Comment/9450891"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query CommentShow($id: ID!) {
    comment(id: $id) {
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
  }' \
  --variables \
  '{
    "id": "gid://shopify/Comment/9450891"
  }'
  ```

  #### Response

  ```json
  {
    "comment": {
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
    }
  }
  ```
