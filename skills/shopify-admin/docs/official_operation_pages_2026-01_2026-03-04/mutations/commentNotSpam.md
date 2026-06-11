---
title: commentNotSpam - GraphQL Admin
description: >-
  Reverses a spam classification on a comment, restoring it to normal moderation
  status. This mutation allows merchants to change their decision when a comment
  has been manually marked as spam.


  For example, when a merchant reviews comments marked as spam and finds a
  legitimate customer question, they can use this mutation to restore the
  comment's normal status and make it eligible for approval.


  Use the `commentNotSpam` mutation to:

  - Unmark comments that were marked as spam

  - Restore comments to normal moderation status

  - Move comments back to the approval queue


  This action changes the comment's status from spam back to pending, where it
  can then be approved or managed according to standard moderation practices.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/commentNotSpam'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/commentNotSpam.md
---

# comment​Not​Spam

mutation

Requires Any of `write_content`, `write_online_store_pages` access scopes.

Reverses a spam classification on a comment, restoring it to normal moderation status. This mutation allows merchants to change their decision when a comment has been manually marked as spam.

For example, when a merchant reviews comments marked as spam and finds a legitimate customer question, they can use this mutation to restore the comment's normal status and make it eligible for approval.

Use the `commentNotSpam` mutation to:

* Unmark comments that were marked as spam
* Restore comments to normal moderation status
* Move comments back to the approval queue

This action changes the comment's status from spam back to pending, where it can then be approved or managed according to standard moderation practices.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the comment to be marked as not spam.

***

## Comment​Not​Spam​Payload returns

* comment

  [Comment](https://shopify.dev/docs/api/admin-graphql/latest/objects/Comment)

  The comment that was marked as not spam.

* user​Errors

  [\[Comment​Not​Spam​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CommentNotSpamUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Marks a comment as not spam

  #### Query

  ```graphql
  mutation CommentNotSpam($id: ID!) {
    commentNotSpam(id: $id) {
      comment {
        id
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
  "query": "mutation CommentNotSpam($id: ID!) { commentNotSpam(id: $id) { comment { id } userErrors { code field message } } }",
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
    mutation CommentNotSpam($id: ID!) {
      commentNotSpam(id: $id) {
        comment {
          id
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
    mutation CommentNotSpam($id: ID!) {
      commentNotSpam(id: $id) {
        comment {
          id
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
    "id": "gid://shopify/Comment/9450891"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation CommentNotSpam($id: ID!) {
        commentNotSpam(id: $id) {
          comment {
            id
          }
          userErrors {
            code
            field
            message
          }
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
  'mutation CommentNotSpam($id: ID!) {
    commentNotSpam(id: $id) {
      comment {
        id
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
    "id": "gid://shopify/Comment/9450891"
  }'
  ```

  #### Response

  ```json
  {
    "commentNotSpam": {
      "comment": {
        "id": "gid://shopify/Comment/9450891"
      },
      "userErrors": []
    }
  }
  ```

* ### commentNotSpam reference
