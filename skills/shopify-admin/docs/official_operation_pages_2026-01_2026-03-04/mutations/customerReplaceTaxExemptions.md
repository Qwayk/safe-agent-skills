---
title: customerReplaceTaxExemptions - GraphQL Admin
description: Replace tax exemptions for a customer.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerReplaceTaxExemptions
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerReplaceTaxExemptions.md
---

# customer​Replace​Tax​Exemptions

mutation

Requires `write_customers` access scope.

Replace tax exemptions for a customer.

## Arguments

* customer​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the customer to update.

* tax​Exemptions

  [\[Tax​Exemption!\]!](https://shopify.dev/docs/api/admin-graphql/latest/enums/TaxExemption)

  required

  The list of tax exemptions that will replace the current exemptions for a customer. Can be an array or a comma-separated list. Example values: `["CA_BC_RESELLER_EXEMPTION", "A_STATUS_CARD_EXEMPTION"]`, `"CA_BC_RESELLER_EXEMPTION, CA_STATUS_CARD_EXEMPTION"`.

***

## Customer​Replace​Tax​Exemptions​Payload returns

* customer

  [Customer](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)

  The updated customer.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Replace tax exemptions for a customer

  #### Query

  ```graphql
  mutation customerReplaceTaxExemptions($customerId: ID!, $taxExemptions: [TaxExemption!]!) {
    customerReplaceTaxExemptions(customerId: $customerId, taxExemptions: $taxExemptions) {
      userErrors {
        field
        message
      }
      customer {
        id
        taxExemptions
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "customerId": "gid://shopify/Customer/554122808",
    "taxExemptions": [
      "CA_MB_COMMERCIAL_FISHERY_EXEMPTION",
      "CA_ON_PURCHASE_EXEMPTION"
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
  "query": "mutation customerReplaceTaxExemptions($customerId: ID!, $taxExemptions: [TaxExemption!]!) { customerReplaceTaxExemptions(customerId: $customerId, taxExemptions: $taxExemptions) { userErrors { field message } customer { id taxExemptions } } }",
   "variables": {
      "customerId": "gid://shopify/Customer/554122808",
      "taxExemptions": [
        "CA_MB_COMMERCIAL_FISHERY_EXEMPTION",
        "CA_ON_PURCHASE_EXEMPTION"
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
    mutation customerReplaceTaxExemptions($customerId: ID!, $taxExemptions: [TaxExemption!]!) {
      customerReplaceTaxExemptions(customerId: $customerId, taxExemptions: $taxExemptions) {
        userErrors {
          field
          message
        }
        customer {
          id
          taxExemptions
        }
      }
    }`,
    {
      variables: {
          "customerId": "gid://shopify/Customer/554122808",
          "taxExemptions": [
              "CA_MB_COMMERCIAL_FISHERY_EXEMPTION",
              "CA_ON_PURCHASE_EXEMPTION"
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
    mutation customerReplaceTaxExemptions($customerId: ID!, $taxExemptions: [TaxExemption!]!) {
      customerReplaceTaxExemptions(customerId: $customerId, taxExemptions: $taxExemptions) {
        userErrors {
          field
          message
        }
        customer {
          id
          taxExemptions
        }
      }
    }
  QUERY

  variables = {
    "customerId": "gid://shopify/Customer/554122808",
    "taxExemptions": [
      "CA_MB_COMMERCIAL_FISHERY_EXEMPTION",
      "CA_ON_PURCHASE_EXEMPTION"
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation customerReplaceTaxExemptions($customerId: ID!, $taxExemptions: [TaxExemption!]!) {
        customerReplaceTaxExemptions(customerId: $customerId, taxExemptions: $taxExemptions) {
          userErrors {
            field
            message
          }
          customer {
            id
            taxExemptions
          }
        }
      }`,
      "variables": {
          "customerId": "gid://shopify/Customer/554122808",
          "taxExemptions": [
              "CA_MB_COMMERCIAL_FISHERY_EXEMPTION",
              "CA_ON_PURCHASE_EXEMPTION"
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation customerReplaceTaxExemptions($customerId: ID!, $taxExemptions: [TaxExemption!]!) {
    customerReplaceTaxExemptions(customerId: $customerId, taxExemptions: $taxExemptions) {
      userErrors {
        field
        message
      }
      customer {
        id
        taxExemptions
      }
    }
  }' \
  --variables \
  '{
    "customerId": "gid://shopify/Customer/554122808",
    "taxExemptions": [
      "CA_MB_COMMERCIAL_FISHERY_EXEMPTION",
      "CA_ON_PURCHASE_EXEMPTION"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "customerReplaceTaxExemptions": {
      "userErrors": [],
      "customer": {
        "id": "gid://shopify/Customer/554122808",
        "taxExemptions": [
          "CA_MB_COMMERCIAL_FISHERY_EXEMPTION",
          "CA_ON_PURCHASE_EXEMPTION"
        ]
      }
    }
  }
  ```

* ### customerReplaceTaxExemptions reference
