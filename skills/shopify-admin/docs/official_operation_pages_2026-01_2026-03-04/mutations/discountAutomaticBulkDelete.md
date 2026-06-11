---
title: discountAutomaticBulkDelete - GraphQL Admin
description: >-
  Deletes multiple automatic discounts in a single operation, providing
  efficient bulk management for stores with extensive discount catalogs. This
  mutation processes deletions asynchronously to handle large volumes without
  blocking other operations.


  For example, when cleaning up expired seasonal promotions or removing outdated
  automatic discounts across product categories, merchants can delete dozens of
  discounts simultaneously rather than processing each individually.


  Use `DiscountAutomaticBulkDelete` to:

  - Remove multiple automatic discounts efficiently

  - Clean up expired or obsolete promotions

  - Streamline discount management workflows

  - Process large-scale discount removals asynchronously


  The operation returns a job object for tracking deletion progress and any
  validation errors encountered during processing.


  Learn more about [discount
  management](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountAutomatic).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticBulkDelete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticBulkDelete.md
---

# discount​Automatic​Bulk​Delete

mutation

Requires Apps must have `write_discounts` access scope.

Deletes multiple automatic discounts in a single operation, providing efficient bulk management for stores with extensive discount catalogs. This mutation processes deletions asynchronously to handle large volumes without blocking other operations.

For example, when cleaning up expired seasonal promotions or removing outdated automatic discounts across product categories, merchants can delete dozens of discounts simultaneously rather than processing each individually.

Use `DiscountAutomaticBulkDelete` to:

* Remove multiple automatic discounts efficiently
* Clean up expired or obsolete promotions
* Streamline discount management workflows
* Process large-scale discount removals asynchronously

The operation returns a job object for tracking deletion progress and any validation errors encountered during processing.

Learn more about [discount management](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountAutomatic).

## Arguments

* ids

  [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The IDs of the automatic discounts to delete.

* saved​Search​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the saved search to use for filtering automatic discounts to delete.

* search

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The search query for filtering automatic discounts to delete.

  For more information on the list of supported fields and search syntax, refer to the [AutomaticDiscountNodes query section](https://shopify.dev/api/admin-graphql/latest/queries/automaticDiscountNodes#argument-automaticdiscountnodes-query).

***

## Discount​Automatic​Bulk​Delete​Payload returns

* job

  [Job](https://shopify.dev/docs/api/admin-graphql/latest/objects/Job)

  The asynchronous job removing the automatic discounts.

* user​Errors

  [\[Discount​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Asynchronously delete automatic discounts in bulk using a search filter

  #### Description

  Asynchronously delete all expired automatic discounts that are type \`percentage\`.

  #### Query

  ```graphql
  mutation discountAutomaticBulkDelete($search: String) {
    discountAutomaticBulkDelete(search: $search) {
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
    "search": "type:percentage status:expired"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation discountAutomaticBulkDelete($search: String) { discountAutomaticBulkDelete(search: $search) { job { id } userErrors { code field message } } }",
   "variables": {
      "search": "type:percentage status:expired"
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
    mutation discountAutomaticBulkDelete($search: String) {
      discountAutomaticBulkDelete(search: $search) {
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
          "search": "type:percentage status:expired"
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
    mutation discountAutomaticBulkDelete($search: String) {
      discountAutomaticBulkDelete(search: $search) {
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
    "search": "type:percentage status:expired"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation discountAutomaticBulkDelete($search: String) {
        discountAutomaticBulkDelete(search: $search) {
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
          "search": "type:percentage status:expired"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation discountAutomaticBulkDelete($search: String) {
    discountAutomaticBulkDelete(search: $search) {
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
    "search": "type:percentage status:expired"
  }'
  ```

  #### Response

  ```json
  {
    "discountAutomaticBulkDelete": {
      "job": {
        "id": "gid://shopify/Job/11a6c2db-7d58-4a77-ac7b-7128dd68b8aa"
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
  mutation discountAutomaticBulkDelete($search: String, $ids: [ID!]) {
    discountAutomaticBulkDelete(search: $search, ids: $ids) {
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
      "gid://shopify/DiscountAutomaticNode/1"
    ],
    "search": "type:bxgy"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation discountAutomaticBulkDelete($search: String, $ids: [ID!]) { discountAutomaticBulkDelete(search: $search, ids: $ids) { job { id } userErrors { code field message } } }",
   "variables": {
      "ids": [
        "gid://shopify/DiscountAutomaticNode/1"
      ],
      "search": "type:bxgy"
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
    mutation discountAutomaticBulkDelete($search: String, $ids: [ID!]) {
      discountAutomaticBulkDelete(search: $search, ids: $ids) {
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
              "gid://shopify/DiscountAutomaticNode/1"
          ],
          "search": "type:bxgy"
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
    mutation discountAutomaticBulkDelete($search: String, $ids: [ID!]) {
      discountAutomaticBulkDelete(search: $search, ids: $ids) {
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
      "gid://shopify/DiscountAutomaticNode/1"
    ],
    "search": "type:bxgy"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation discountAutomaticBulkDelete($search: String, $ids: [ID!]) {
        discountAutomaticBulkDelete(search: $search, ids: $ids) {
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
              "gid://shopify/DiscountAutomaticNode/1"
          ],
          "search": "type:bxgy"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation discountAutomaticBulkDelete($search: String, $ids: [ID!]) {
    discountAutomaticBulkDelete(search: $search, ids: $ids) {
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
      "gid://shopify/DiscountAutomaticNode/1"
    ],
    "search": "type:bxgy"
  }'
  ```

  #### Response

  ```json
  {
    "discountAutomaticBulkDelete": {
      "job": null,
      "userErrors": [
        {
          "code": "TOO_MANY_ARGUMENTS",
          "field": null,
          "message": "Only one of IDs, search argument or saved search ID is allowed."
        }
      ]
    }
  }
  ```

* ### discountAutomaticBulkDelete reference
