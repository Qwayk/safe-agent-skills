---
title: discountCodeRedeemCodeBulkDelete - GraphQL Admin
description: >-
  Asynchronously delete

  [discount
  codes](https://help.shopify.com/manual/discounts/discount-types#discount-codes)

  in bulk that customers can use to redeem a discount.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeRedeemCodeBulkDelete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeRedeemCodeBulkDelete.md
---

# discount​Code​Redeem​Code​Bulk​Delete

mutation

Requires Apps must have `write_discounts` access scope.

Asynchronously delete [discount codes](https://help.shopify.com/manual/discounts/discount-types#discount-codes) in bulk that customers can use to redeem a discount.

## Arguments

* discount​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the [`DiscountCodeNode`](https://help.shopify.com/docs/api/admin-graphql/latest/objects/DiscountCodeNode#field-id) object that the codes will be removed from. For example, `gid://shopify/DiscountCodeNode/123`. You can use the [`codeDiscountNodes` query](https://shopify.dev/docs/api/admin-graphql/latest/queries/codeDiscountNodes) to retrieve the ID.

* ids

  [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The IDs of the [`DiscountRedeemCode`](https://shopify.dev/docs/api/admin-graphql/latest/objects/discountredeemcode#field-id) objects to delete. For example, `gid://shopify/DiscountRedeemCode/123`. You can use the [`codeDiscountNodes` query](https://shopify.dev/docs/api/admin-graphql/latest/queries/codeDiscountNodes) to retrieve the ID.

* saved​Search​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of a [saved search](https://shopify.dev/docs/api/admin-graphql/latest/objects/savedsearch#field-id).

* search

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  A filter made up of terms, connectives, modifiers, and comparators that you can use to search for code discounts. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/docs/api/usage/search-syntax).

  For a list of accepted values for the `search` field, refer to the [`query` argument on the `codeDiscountNodes` query](https://shopify.dev/docs/api/admin-graphql/latest/queries/codeDiscountNodes#argument-query).

***

## Discount​Code​Redeem​Code​Bulk​Delete​Payload returns

* job

  [Job](https://shopify.dev/docs/api/admin-graphql/latest/objects/Job)

  The asynchronous job that deletes the discount codes.

* user​Errors

  [\[Discount​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Asynchronously delete discount redeem codes in bulk using a search filter

  #### Description

  Asynchronously delete all redeem codes that have never been used.

  #### Query

  ```graphql
  mutation discountCodeRedeemCodeBulkDelete($discountId: ID!, $search: String) {
    discountCodeRedeemCodeBulkDelete(discountId: $discountId, search: $search) {
      job {
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
    "discountId": "gid://shopify/DiscountCodeNode/2429471",
    "search": "times_used:0"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation discountCodeRedeemCodeBulkDelete($discountId: ID!, $search: String) { discountCodeRedeemCodeBulkDelete(discountId: $discountId, search: $search) { job { id } userErrors { code field message } } }",
   "variables": {
      "discountId": "gid://shopify/DiscountCodeNode/2429471",
      "search": "times_used:0"
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
    mutation discountCodeRedeemCodeBulkDelete($discountId: ID!, $search: String) {
      discountCodeRedeemCodeBulkDelete(discountId: $discountId, search: $search) {
        job {
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
          "discountId": "gid://shopify/DiscountCodeNode/2429471",
          "search": "times_used:0"
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
    mutation discountCodeRedeemCodeBulkDelete($discountId: ID!, $search: String) {
      discountCodeRedeemCodeBulkDelete(discountId: $discountId, search: $search) {
        job {
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
    "discountId": "gid://shopify/DiscountCodeNode/2429471",
    "search": "times_used:0"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation discountCodeRedeemCodeBulkDelete($discountId: ID!, $search: String) {
        discountCodeRedeemCodeBulkDelete(discountId: $discountId, search: $search) {
          job {
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
          "discountId": "gid://shopify/DiscountCodeNode/2429471",
          "search": "times_used:0"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation discountCodeRedeemCodeBulkDelete($discountId: ID!, $search: String) {
    discountCodeRedeemCodeBulkDelete(discountId: $discountId, search: $search) {
      job {
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
    "discountId": "gid://shopify/DiscountCodeNode/2429471",
    "search": "times_used:0"
  }'
  ```

  #### Response

  ```json
  {
    "discountCodeRedeemCodeBulkDelete": {
      "job": {
        "id": "gid://shopify/Job/a2337b55-0b31-44d9-9027-f4fefc5317d5"
      },
      "userErrors": []
    }
  }
  ```

* ### Deletes a discount code

  #### Query

  ```graphql
  mutation DiscountRedeemCodeBulkDelete($discountId: ID!, $ids: [ID!]) {
    discountCodeRedeemCodeBulkDelete(discountId: $discountId, ids: $ids) {
      job {
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
    "discountId": "gid://shopify/DiscountCodeNode/2429471",
    "ids": [
      "gid://shopify/DiscountRedeemCode/1"
    ]
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation DiscountRedeemCodeBulkDelete($discountId: ID!, $ids: [ID!]) { discountCodeRedeemCodeBulkDelete(discountId: $discountId, ids: $ids) { job { id } userErrors { code field message } } }",
   "variables": {
      "discountId": "gid://shopify/DiscountCodeNode/2429471",
      "ids": [
        "gid://shopify/DiscountRedeemCode/1"
      ]
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
    mutation DiscountRedeemCodeBulkDelete($discountId: ID!, $ids: [ID!]) {
      discountCodeRedeemCodeBulkDelete(discountId: $discountId, ids: $ids) {
        job {
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
          "discountId": "gid://shopify/DiscountCodeNode/2429471",
          "ids": [
              "gid://shopify/DiscountRedeemCode/1"
          ]
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
    mutation DiscountRedeemCodeBulkDelete($discountId: ID!, $ids: [ID!]) {
      discountCodeRedeemCodeBulkDelete(discountId: $discountId, ids: $ids) {
        job {
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
    "discountId": "gid://shopify/DiscountCodeNode/2429471",
    "ids": [
      "gid://shopify/DiscountRedeemCode/1"
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation DiscountRedeemCodeBulkDelete($discountId: ID!, $ids: [ID!]) {
        discountCodeRedeemCodeBulkDelete(discountId: $discountId, ids: $ids) {
          job {
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
          "discountId": "gid://shopify/DiscountCodeNode/2429471",
          "ids": [
              "gid://shopify/DiscountRedeemCode/1"
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation DiscountRedeemCodeBulkDelete($discountId: ID!, $ids: [ID!]) {
    discountCodeRedeemCodeBulkDelete(discountId: $discountId, ids: $ids) {
      job {
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
    "discountId": "gid://shopify/DiscountCodeNode/2429471",
    "ids": [
      "gid://shopify/DiscountRedeemCode/1"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "discountCodeRedeemCodeBulkDelete": {
      "job": {
        "id": "gid://shopify/Job/33cb59e4-a258-4b33-af81-09b196ad4385"
      },
      "userErrors": []
    }
  }
  ```

* ### Using more than one targeting argument returns an error

  #### Description

  Trying to use both \`search\` and \`ids\` arguments returns an error

  #### Query

  ```graphql
  mutation discountCodeRedeemCodeBulkDelete($discountId: ID!, $search: String, $ids: [ID!]) {
    discountCodeRedeemCodeBulkDelete(discountId: $discountId, search: $search, ids: $ids) {
      job {
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
    "discountId": "gid://shopify/DiscountCodeNode/2429471",
    "ids": [
      "gid://shopify/DiscountRedeemCode/1"
    ],
    "search": "discount_type:bxgy"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation discountCodeRedeemCodeBulkDelete($discountId: ID!, $search: String, $ids: [ID!]) { discountCodeRedeemCodeBulkDelete(discountId: $discountId, search: $search, ids: $ids) { job { id } userErrors { code field message } } }",
   "variables": {
      "discountId": "gid://shopify/DiscountCodeNode/2429471",
      "ids": [
        "gid://shopify/DiscountRedeemCode/1"
      ],
      "search": "discount_type:bxgy"
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
    mutation discountCodeRedeemCodeBulkDelete($discountId: ID!, $search: String, $ids: [ID!]) {
      discountCodeRedeemCodeBulkDelete(discountId: $discountId, search: $search, ids: $ids) {
        job {
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
          "discountId": "gid://shopify/DiscountCodeNode/2429471",
          "ids": [
              "gid://shopify/DiscountRedeemCode/1"
          ],
          "search": "discount_type:bxgy"
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
    mutation discountCodeRedeemCodeBulkDelete($discountId: ID!, $search: String, $ids: [ID!]) {
      discountCodeRedeemCodeBulkDelete(discountId: $discountId, search: $search, ids: $ids) {
        job {
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
    "discountId": "gid://shopify/DiscountCodeNode/2429471",
    "ids": [
      "gid://shopify/DiscountRedeemCode/1"
    ],
    "search": "discount_type:bxgy"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation discountCodeRedeemCodeBulkDelete($discountId: ID!, $search: String, $ids: [ID!]) {
        discountCodeRedeemCodeBulkDelete(discountId: $discountId, search: $search, ids: $ids) {
          job {
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
          "discountId": "gid://shopify/DiscountCodeNode/2429471",
          "ids": [
              "gid://shopify/DiscountRedeemCode/1"
          ],
          "search": "discount_type:bxgy"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation discountCodeRedeemCodeBulkDelete($discountId: ID!, $search: String, $ids: [ID!]) {
    discountCodeRedeemCodeBulkDelete(discountId: $discountId, search: $search, ids: $ids) {
      job {
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
    "discountId": "gid://shopify/DiscountCodeNode/2429471",
    "ids": [
      "gid://shopify/DiscountRedeemCode/1"
    ],
    "search": "discount_type:bxgy"
  }'
  ```

  #### Response

  ```json
  {
    "discountCodeRedeemCodeBulkDelete": {
      "job": null,
      "userErrors": [
        {
          "code": "TOO_MANY_ARGUMENTS",
          "field": null,
          "message": "Only one of 'ids', 'search' or 'saved_search_id' is allowed."
        }
      ]
    }
  }
  ```

* ### discountCodeRedeemCodeBulkDelete reference
