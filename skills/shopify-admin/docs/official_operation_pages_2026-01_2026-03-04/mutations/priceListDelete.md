---
title: priceListDelete - GraphQL Admin
description: >-
  Deletes a price list. For example, you can delete a price list so that it no
  longer applies for products in the associated market.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/priceListDelete'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/priceListDelete.md
---

# price​List​Delete

mutation

Requires `write_products` access scope. Also: The user must have permission to delete catalogs.

Deletes a price list. For example, you can delete a price list so that it no longer applies for products in the associated market.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the price list to be deleted.

***

## Price​List​Delete​Payload returns

* deleted​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the deleted price list.

* user​Errors

  [\[Price​List​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PriceListUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Delete a price list

  #### Description

  Deleting a price list returns the ID of the deleted price list

  #### Query

  ```graphql
  mutation priceListDelete($id: ID!) {
    priceListDelete(id: $id) {
      deletedId
      userErrors {
        field
        code
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/PriceList/294167858"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation priceListDelete($id: ID!) { priceListDelete(id: $id) { deletedId userErrors { field code message } } }",
   "variables": {
      "id": "gid://shopify/PriceList/294167858"
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
    mutation priceListDelete($id: ID!) {
      priceListDelete(id: $id) {
        deletedId
        userErrors {
          field
          code
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/PriceList/294167858"
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
    mutation priceListDelete($id: ID!) {
      priceListDelete(id: $id) {
        deletedId
        userErrors {
          field
          code
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/PriceList/294167858"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation priceListDelete($id: ID!) {
        priceListDelete(id: $id) {
          deletedId
          userErrors {
            field
            code
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/PriceList/294167858"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation priceListDelete($id: ID!) {
    priceListDelete(id: $id) {
      deletedId
      userErrors {
        field
        code
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/PriceList/294167858"
  }'
  ```

  #### Response

  ```json
  {
    "priceListDelete": {
      "deletedId": "gid://shopify/PriceList/294167858",
      "userErrors": []
    }
  }
  ```

* ### priceListDelete reference
