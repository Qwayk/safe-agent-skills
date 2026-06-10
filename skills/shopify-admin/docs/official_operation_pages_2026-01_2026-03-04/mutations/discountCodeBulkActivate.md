---
title: discountCodeBulkActivate - GraphQL Admin
description: >-
  Activates multiple [code
  discounts](https://help.shopify.com/manual/discounts/discount-types#discount-codes)
  asynchronously using one of the following:

  - A search query

  - A saved search ID

  - A list of discount code IDs


  For example, you can activate discounts for all codes that match a search
  criteria, or activate a predefined set of discount codes.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeBulkActivate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeBulkActivate.md
---

# discount​Code​Bulk​Activate

mutation

Requires Apps must have `write_discounts` access scope.

Activates multiple [code discounts](https://help.shopify.com/manual/discounts/discount-types#discount-codes) asynchronously using one of the following:

* A search query
* A saved search ID
* A list of discount code IDs

For example, you can activate discounts for all codes that match a search criteria, or activate a predefined set of discount codes.

## Arguments

* ids

  [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The IDs of the discounts to activate.

* saved​Search​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the saved search for filtering discounts to activate. Saved searches represent [customer segments](https://help.shopify.com/manual/customers/customer-segments) that merchants have built in the Shopify admin.

* search

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The search query for filtering discounts.\
  \
  For more information on the list of supported fields and search syntax, refer to the [`codeDiscountNodes`](https://shopify.dev/docs/api/admin-graphql/latest/queries/codeDiscountNodes#query-arguments) query.

***

## Discount​Code​Bulk​Activate​Payload returns

* job

  [Job](https://shopify.dev/docs/api/admin-graphql/latest/objects/Job)

  The asynchronous job that activates the discounts.

* user​Errors

  [\[Discount​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Asynchronously activate code discounts in bulk using a search filter

  #### Description

  Asynchronously activate all code discounts that start within the past week and are type \`percentage\`.

  #### Query

  ```graphql
  mutation discountCodeBulkActivate($search: String) {
    discountCodeBulkActivate(search: $search) {
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
    "search": "discount_type:percentage starts_at:past_week"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation discountCodeBulkActivate($search: String) { discountCodeBulkActivate(search: $search) { job { id } userErrors { code field message } } }",
   "variables": {
      "search": "discount_type:percentage starts_at:past_week"
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
    mutation discountCodeBulkActivate($search: String) {
      discountCodeBulkActivate(search: $search) {
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
          "search": "discount_type:percentage starts_at:past_week"
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
    mutation discountCodeBulkActivate($search: String) {
      discountCodeBulkActivate(search: $search) {
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
    "search": "discount_type:percentage starts_at:past_week"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation discountCodeBulkActivate($search: String) {
        discountCodeBulkActivate(search: $search) {
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
          "search": "discount_type:percentage starts_at:past_week"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation discountCodeBulkActivate($search: String) {
    discountCodeBulkActivate(search: $search) {
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
    "search": "discount_type:percentage starts_at:past_week"
  }'
  ```

  #### Response

  ```json
  {
    "discountCodeBulkActivate": {
      "job": {
        "id": "gid://shopify/Job/2c09b7e9-e9b3-435a-8ab4-2c35f3eeb6b1"
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
  mutation discountCodeBulkActivate($search: String, $ids: [ID!]) {
    discountCodeBulkActivate(search: $search, ids: $ids) {
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
  "query": "mutation discountCodeBulkActivate($search: String, $ids: [ID!]) { discountCodeBulkActivate(search: $search, ids: $ids) { job { id } userErrors { code field message } } }",
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
    mutation discountCodeBulkActivate($search: String, $ids: [ID!]) {
      discountCodeBulkActivate(search: $search, ids: $ids) {
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
    mutation discountCodeBulkActivate($search: String, $ids: [ID!]) {
      discountCodeBulkActivate(search: $search, ids: $ids) {
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
      "query": `mutation discountCodeBulkActivate($search: String, $ids: [ID!]) {
        discountCodeBulkActivate(search: $search, ids: $ids) {
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
  'mutation discountCodeBulkActivate($search: String, $ids: [ID!]) {
    discountCodeBulkActivate(search: $search, ids: $ids) {
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
    "discountCodeBulkActivate": {
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

* ### discountCodeBulkActivate reference
