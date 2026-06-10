---
title: companyContactCreate - GraphQL Admin
description: Creates a company contact and the associated customer.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/companyContactCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/companyContactCreate.md
---

# company​Contact​Create

mutation

Requires `write_customers` access scope or `write_companies` access scope. Also: The API client must be installed on a Shopify Plus store.

Creates a company contact and the associated customer.

## Arguments

* company​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the company that the company contact belongs to.

* input

  [Company​Contact​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CompanyContactInput)

  required

  The fields to use to create the company contact.

***

## Company​Contact​Create​Payload returns

* company​Contact

  [Company​Contact](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyContact)

  The created company contact.

* user​Errors

  [\[Business​Customer​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/BusinessCustomerUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a company contact

  #### Description

  Create a company contact for the specified company.

  #### Query

  ```graphql
  mutation CompanyContactCreate($companyId: ID!, $input: CompanyContactInput!) {
    companyContactCreate(companyId: $companyId, input: $input) {
      companyContact {
        id
        company {
          id
          name
        }
        customer {
          id
          firstName
          lastName
          email
        }
      }
      userErrors {
        field
        message
        code
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "companyId": "gid://shopify/Company/426793626",
    "input": {
      "email": "avery.brown@example.com",
      "firstName": "Avery",
      "lastName": "Brown"
    }
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation CompanyContactCreate($companyId: ID!, $input: CompanyContactInput!) { companyContactCreate(companyId: $companyId, input: $input) { companyContact { id company { id name } customer { id firstName lastName email } } userErrors { field message code } } }",
   "variables": {
      "companyId": "gid://shopify/Company/426793626",
      "input": {
        "email": "avery.brown@example.com",
        "firstName": "Avery",
        "lastName": "Brown"
      }
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
    mutation CompanyContactCreate($companyId: ID!, $input: CompanyContactInput!) {
      companyContactCreate(companyId: $companyId, input: $input) {
        companyContact {
          id
          company {
            id
            name
          }
          customer {
            id
            firstName
            lastName
            email
          }
        }
        userErrors {
          field
          message
          code
        }
      }
    }`,
    {
      variables: {
          "companyId": "gid://shopify/Company/426793626",
          "input": {
              "email": "avery.brown@example.com",
              "firstName": "Avery",
              "lastName": "Brown"
          }
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
    mutation CompanyContactCreate($companyId: ID!, $input: CompanyContactInput!) {
      companyContactCreate(companyId: $companyId, input: $input) {
        companyContact {
          id
          company {
            id
            name
          }
          customer {
            id
            firstName
            lastName
            email
          }
        }
        userErrors {
          field
          message
          code
        }
      }
    }
  QUERY

  variables = {
    "companyId": "gid://shopify/Company/426793626",
    "input": {
      "email": "avery.brown@example.com",
      "firstName": "Avery",
      "lastName": "Brown"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation CompanyContactCreate($companyId: ID!, $input: CompanyContactInput!) {
        companyContactCreate(companyId: $companyId, input: $input) {
          companyContact {
            id
            company {
              id
              name
            }
            customer {
              id
              firstName
              lastName
              email
            }
          }
          userErrors {
            field
            message
            code
          }
        }
      }`,
      "variables": {
          "companyId": "gid://shopify/Company/426793626",
          "input": {
              "email": "avery.brown@example.com",
              "firstName": "Avery",
              "lastName": "Brown"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation CompanyContactCreate($companyId: ID!, $input: CompanyContactInput!) {
    companyContactCreate(companyId: $companyId, input: $input) {
      companyContact {
        id
        company {
          id
          name
        }
        customer {
          id
          firstName
          lastName
          email
        }
      }
      userErrors {
        field
        message
        code
      }
    }
  }' \
  --variables \
  '{
    "companyId": "gid://shopify/Company/426793626",
    "input": {
      "email": "avery.brown@example.com",
      "firstName": "Avery",
      "lastName": "Brown"
    }
  }'
  ```

  #### Response

  ```json
  {
    "companyContactCreate": {
      "companyContact": {
        "id": "gid://shopify/CompanyContact/1059341859",
        "company": {
          "id": "gid://shopify/Company/426793626",
          "name": "Fancy Pants Inc."
        },
        "customer": {
          "id": "gid://shopify/Customer/1073339480",
          "firstName": "Avery",
          "lastName": "Brown",
          "email": "avery.brown@example.com"
        }
      },
      "userErrors": []
    }
  }
  ```

* ### companyContactCreate reference
