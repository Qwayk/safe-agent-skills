---
title: commentApprove - GraphQL Admin
description: >-
  Approves a pending comment, making it visible to store visitors on the
  associated blog article.


  For example, when a customer submits a question about a product in a blog
  post, merchants can approve the comment to make it publicly visible.


  Use the `commentApprove` mutation to:

  - Publish pending comments after review

  - Enable customer discussions on blog articles

  - Maintain quality control over comments


  Once approved, the comment becomes visible to all store visitors.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/commentApprove'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/commentApprove.md
---

# comment​Approve

mutation

Requires Any of `write_content`, `write_online_store_pages` access scopes.

Approves a pending comment, making it visible to store visitors on the associated blog article.

For example, when a customer submits a question about a product in a blog post, merchants can approve the comment to make it publicly visible.

Use the `commentApprove` mutation to:

* Publish pending comments after review
* Enable customer discussions on blog articles
* Maintain quality control over comments

Once approved, the comment becomes visible to all store visitors.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the comment to be approved.

***

## Comment​Approve​Payload returns

* comment

  [Comment](https://shopify.dev/docs/api/admin-graphql/latest/objects/Comment)

  The comment that was approved.

* user​Errors

  [\[Comment​Approve​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CommentApproveUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Approves a comment

  #### Query

  ```graphql
  mutation ApproveComment($id: ID!) {
    commentApprove(id: $id) {
      comment {
        id
        status
      }
      userErrors {
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/Comment/757536350"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation ApproveComment($id: ID!) { commentApprove(id: $id) { comment { id status } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/Comment/757536350"
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
    mutation ApproveComment($id: ID!) {
      commentApprove(id: $id) {
        comment {
          id
          status
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/Comment/757536350"
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
    mutation ApproveComment($id: ID!) {
      commentApprove(id: $id) {
        comment {
          id
          status
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/Comment/757536350"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation ApproveComment($id: ID!) {
        commentApprove(id: $id) {
          comment {
            id
            status
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Comment/757536350"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation ApproveComment($id: ID!) {
    commentApprove(id: $id) {
      comment {
        id
        status
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/Comment/757536350"
  }'
  ```

  #### Response

  ```json
  {
    "commentApprove": {
      "comment": {
        "id": "gid://shopify/Comment/757536350",
        "status": "PUBLISHED"
      },
      "userErrors": []
    }
  }
  ```

* ### commentApprove reference
