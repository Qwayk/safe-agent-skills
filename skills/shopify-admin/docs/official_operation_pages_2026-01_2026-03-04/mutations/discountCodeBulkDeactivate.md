---
title: discountCodeBulkDeactivate - GraphQL Admin
description: >-
  Deactivates multiple [code-based
  discounts](https://help.shopify.com/manual/discounts/discount-types#discount-codes)
  asynchronously using one of the following:

  - A search query

  - A saved search ID

  - A list of discount code IDs


  For example, you can deactivate discounts for all codes that match a search
  criteria, or deactivate a predefined set of discount codes.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeBulkDeactivate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeBulkDeactivate.md
---

# discount​Code​Bulk​Deactivate

mutation

Requires Apps must have `write_discounts` access scope.

Deactivates multiple [code-based discounts](https://help.shopify.com/manual/discounts/discount-types#discount-codes) asynchronously using one of the following:

* A search query
* A saved search ID
* A list of discount code IDs

For example, you can deactivate discounts for all codes that match a search criteria, or deactivate a predefined set of discount codes.

## Arguments

* ids

  [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The IDs of the discounts to deactivate.

* saved​Search​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the saved search for filtering discounts to deactivate. Saved searches represent [customer segments](https://help.shopify.com/manual/customers/customer-segments) that merchants have built in the Shopify admin.

* search

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The search query for filtering discounts.\
  \
  For more information on the list of supported fields and search syntax, refer to the [`codeDiscountNodes`](https://shopify.dev/docs/api/admin-graphql/latest/queries/codeDiscountNodes#query-arguments) query.

***

## Discount​Code​Bulk​Deactivate​Payload returns

* job

  [Job](https://shopify.dev/docs/api/admin-graphql/latest/objects/Job)

  The asynchronous job that deactivates the discounts.

* user​Errors

  [\[Discount​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Asynchronously deactivate code discounts in bulk using a search filter

  #### Description

  Asynchronously deactivate all \[code discounts]\(https://help.shopify.com/manual/discounts/discount-types#discount-codes) that expired in the past week and provide a percentage off the products in an order.

  #### Query

  ```graphql
  mutation discountCodeBulkDeactivate($search: String) {
    discountCodeBulkDeactivate(search: $search) {
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
    "search": "discount_type:percentage ends_at:past_week"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation discountCodeBulkDeactivate($search: String) { discountCodeBulkDeactivate(search: $search) { job { id } userErrors { code field message } } }",
   "variables": {
      "search": "discount_type:percentage ends_at:past_week"
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
    mutation discountCodeBulkDeactivate($search: String) {
      discountCodeBulkDeactivate(search: $search) {
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
          "search": "discount_type:percentage ends_at:past_week"
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
    mutation discountCodeBulkDeactivate($search: String) {
      discountCodeBulkDeactivate(search: $search) {
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
    "search": "discount_type:percentage ends_at:past_week"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation discountCodeBulkDeactivate($search: String) {
        discountCodeBulkDeactivate(search: $search) {
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
          "search": "discount_type:percentage ends_at:past_week"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation discountCodeBulkDeactivate($search: String) {
    discountCodeBulkDeactivate(search: $search) {
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
    "search": "discount_type:percentage ends_at:past_week"
  }'
  ```

  #### Response

  ```json
  {
    "discountCodeBulkDeactivate": {
      "job": {
        "id": "gid://shopify/Job/54e3ab26-1701-4c10-b582-875adb274811"
      },
      "userErrors": []
    }
  }
  ```

* ### Using more than one argument returns an error

  #### Description

  If you use both \`search\` and \`ids\` arguments in the same request, then the mutation returns an error.

  #### Query

  ```graphql
  mutation discountCodeBulkDeactivate($search: String, $ids: [ID!]) {
    discountCodeBulkDeactivate(search: $search, ids: $ids) {
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
    "ids": [
      "gid://shopify/DiscountCodeNode/1"
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
  "query": "mutation discountCodeBulkDeactivate($search: String, $ids: [ID!]) { discountCodeBulkDeactivate(search: $search, ids: $ids) { job { id } userErrors { code field message } } }",
   "variables": {
      "ids": [
        "gid://shopify/DiscountCodeNode/1"
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
    mutation discountCodeBulkDeactivate($search: String, $ids: [ID!]) {
      discountCodeBulkDeactivate(search: $search, ids: $ids) {
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
          "ids": [
              "gid://shopify/DiscountCodeNode/1"
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
    mutation discountCodeBulkDeactivate($search: String, $ids: [ID!]) {
      discountCodeBulkDeactivate(search: $search, ids: $ids) {
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
    "ids": [
      "gid://shopify/DiscountCodeNode/1"
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
      "query": `mutation discountCodeBulkDeactivate($search: String, $ids: [ID!]) {
        discountCodeBulkDeactivate(search: $search, ids: $ids) {
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
          "ids": [
              "gid://shopify/DiscountCodeNode/1"
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
  'mutation discountCodeBulkDeactivate($search: String, $ids: [ID!]) {
    discountCodeBulkDeactivate(search: $search, ids: $ids) {
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
    "ids": [
      "gid://shopify/DiscountCodeNode/1"
    ],
    "search": "discount_type:bxgy"
  }'
  ```

  #### Response

  ```json
  {
    "discountCodeBulkDeactivate": {
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

* ### discountCodeBulkDeactivate reference
