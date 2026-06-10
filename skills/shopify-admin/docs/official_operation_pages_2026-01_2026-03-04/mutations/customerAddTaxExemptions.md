---
title: customerAddTaxExemptions - GraphQL Admin
description: Add tax exemptions for the customer.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerAddTaxExemptions
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerAddTaxExemptions.md
---

# customer​Add​Tax​Exemptions

mutation

Requires `write_customers` access scope.

Add tax exemptions for the customer.

## Arguments

* customer​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the customer to update.

* tax​Exemptions

  [\[Tax​Exemption!\]!](https://shopify.dev/docs/api/admin-graphql/latest/enums/TaxExemption)

  required

  The list of tax exemptions to add for the customer, in the format of an array or a comma-separated list. Example values: `["CA_BC_RESELLER_EXEMPTION", "CA_STATUS_CARD_EXEMPTION"]`, `"CA_BC_RESELLER_EXEMPTION, CA_STATUS_CARD_EXEMPTION"`.

***

## Customer​Add​Tax​Exemptions​Payload returns

* customer

  [Customer](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)

  The updated customer.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Add tax exemptions for a customer

  #### Query

  ```graphql
  mutation customerAddTaxExemptions($customerId: ID!, $taxExemptions: [TaxExemption!]!) {
    customerAddTaxExemptions(customerId: $customerId, taxExemptions: $taxExemptions) {
      userErrors {
        field
        message
      }
      customer {
        id
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "customerId": "gid://shopify/Customer/839649557",
    "taxExemptions": [
      "CA_BC_RESELLER_EXEMPTION",
      "CA_STATUS_CARD_EXEMPTION"
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
  "query": "mutation customerAddTaxExemptions($customerId: ID!, $taxExemptions: [TaxExemption!]!) { customerAddTaxExemptions(customerId: $customerId, taxExemptions: $taxExemptions) { userErrors { field message } customer { id } } }",
   "variables": {
      "customerId": "gid://shopify/Customer/839649557",
      "taxExemptions": [
        "CA_BC_RESELLER_EXEMPTION",
        "CA_STATUS_CARD_EXEMPTION"
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
    mutation customerAddTaxExemptions($customerId: ID!, $taxExemptions: [TaxExemption!]!) {
      customerAddTaxExemptions(customerId: $customerId, taxExemptions: $taxExemptions) {
        userErrors {
          field
          message
        }
        customer {
          id
        }
      }
    }`,
    {
      variables: {
          "customerId": "gid://shopify/Customer/839649557",
          "taxExemptions": [
              "CA_BC_RESELLER_EXEMPTION",
              "CA_STATUS_CARD_EXEMPTION"
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
    mutation customerAddTaxExemptions($customerId: ID!, $taxExemptions: [TaxExemption!]!) {
      customerAddTaxExemptions(customerId: $customerId, taxExemptions: $taxExemptions) {
        userErrors {
          field
          message
        }
        customer {
          id
        }
      }
    }
  QUERY

  variables = {
    "customerId": "gid://shopify/Customer/839649557",
    "taxExemptions": [
      "CA_BC_RESELLER_EXEMPTION",
      "CA_STATUS_CARD_EXEMPTION"
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation customerAddTaxExemptions($customerId: ID!, $taxExemptions: [TaxExemption!]!) {
        customerAddTaxExemptions(customerId: $customerId, taxExemptions: $taxExemptions) {
          userErrors {
            field
            message
          }
          customer {
            id
          }
        }
      }`,
      "variables": {
          "customerId": "gid://shopify/Customer/839649557",
          "taxExemptions": [
              "CA_BC_RESELLER_EXEMPTION",
              "CA_STATUS_CARD_EXEMPTION"
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation customerAddTaxExemptions($customerId: ID!, $taxExemptions: [TaxExemption!]!) {
    customerAddTaxExemptions(customerId: $customerId, taxExemptions: $taxExemptions) {
      userErrors {
        field
        message
      }
      customer {
        id
      }
    }
  }' \
  --variables \
  '{
    "customerId": "gid://shopify/Customer/839649557",
    "taxExemptions": [
      "CA_BC_RESELLER_EXEMPTION",
      "CA_STATUS_CARD_EXEMPTION"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "customerAddTaxExemptions": {
      "userErrors": [],
      "customer": {
        "id": "gid://shopify/Customer/839649557"
      }
    }
  }
  ```

* ### customerAddTaxExemptions reference
