---
title: customerCreate - GraphQL Admin
description: >-
  Creates a new
  [`Customer`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)
  in the store.


  Accepts customer details including contact information, marketing consent
  preferences, and tax exemptions through the
  [`CustomerInput`](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CustomerInput)
  input object. You can also associate
  [`metafields`](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MetafieldInput)
  and tags to organize and extend customer data.


  Apps using protected customer data must meet Shopify's [protected customer
  data
  requirements](https://shopify.dev/docs/apps/launch/protected-customer-data#requirements).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerCreate'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerCreate.md
---

# customer​Create

mutation

Requires `write_customers` access scope.

Creates a new [`Customer`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer) in the store.

Accepts customer details including contact information, marketing consent preferences, and tax exemptions through the [`CustomerInput`](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CustomerInput) input object. You can also associate [`metafields`](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MetafieldInput) and tags to organize and extend customer data.

Apps using protected customer data must meet Shopify's [protected customer data requirements](https://shopify.dev/docs/apps/launch/protected-customer-data#requirements).

## Arguments

* input

  [Customer​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CustomerInput)

  required

  The input fields to create a customer.

***

## Customer​Create​Payload returns

* customer

  [Customer](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)

  The created customer.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a customer subscribed to SMS marketing

  #### Description

  Create a customer and subscribe them to SMS marketing.

  #### Query

  ```graphql
  mutation customerCreate($input: CustomerInput!) {
    customerCreate(input: $input) {
      userErrors {
        field
        message
      }
      customer {
        id
        email
        phone
        taxExempt
        firstName
        lastName
        amountSpent {
          amount
          currencyCode
        }
        smsMarketingConsent {
          marketingState
          marketingOptInLevel
          consentUpdatedAt
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "email": "steve.lastnameson@example.com",
      "phone": "+16465555555",
      "firstName": "Steve",
      "smsMarketingConsent": {
        "marketingState": "SUBSCRIBED",
        "marketingOptInLevel": "SINGLE_OPT_IN"
      }
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
  "query": "mutation customerCreate($input: CustomerInput!) { customerCreate(input: $input) { userErrors { field message } customer { id email phone taxExempt firstName lastName amountSpent { amount currencyCode } smsMarketingConsent { marketingState marketingOptInLevel consentUpdatedAt } } } }",
   "variables": {
      "input": {
        "email": "steve.lastnameson@example.com",
        "phone": "+16465555555",
        "firstName": "Steve",
        "smsMarketingConsent": {
          "marketingState": "SUBSCRIBED",
          "marketingOptInLevel": "SINGLE_OPT_IN"
        }
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
    mutation customerCreate($input: CustomerInput!) {
      customerCreate(input: $input) {
        userErrors {
          field
          message
        }
        customer {
          id
          email
          phone
          taxExempt
          firstName
          lastName
          amountSpent {
            amount
            currencyCode
          }
          smsMarketingConsent {
            marketingState
            marketingOptInLevel
            consentUpdatedAt
          }
        }
      }
    }`,
    {
      variables: {
          "input": {
              "email": "steve.lastnameson@example.com",
              "phone": "+16465555555",
              "firstName": "Steve",
              "smsMarketingConsent": {
                  "marketingState": "SUBSCRIBED",
                  "marketingOptInLevel": "SINGLE_OPT_IN"
              }
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
    mutation customerCreate($input: CustomerInput!) {
      customerCreate(input: $input) {
        userErrors {
          field
          message
        }
        customer {
          id
          email
          phone
          taxExempt
          firstName
          lastName
          amountSpent {
            amount
            currencyCode
          }
          smsMarketingConsent {
            marketingState
            marketingOptInLevel
            consentUpdatedAt
          }
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "email": "steve.lastnameson@example.com",
      "phone": "+16465555555",
      "firstName": "Steve",
      "smsMarketingConsent": {
        "marketingState": "SUBSCRIBED",
        "marketingOptInLevel": "SINGLE_OPT_IN"
      }
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation customerCreate($input: CustomerInput!) {
        customerCreate(input: $input) {
          userErrors {
            field
            message
          }
          customer {
            id
            email
            phone
            taxExempt
            firstName
            lastName
            amountSpent {
              amount
              currencyCode
            }
            smsMarketingConsent {
              marketingState
              marketingOptInLevel
              consentUpdatedAt
            }
          }
        }
      }`,
      "variables": {
          "input": {
              "email": "steve.lastnameson@example.com",
              "phone": "+16465555555",
              "firstName": "Steve",
              "smsMarketingConsent": {
                  "marketingState": "SUBSCRIBED",
                  "marketingOptInLevel": "SINGLE_OPT_IN"
              }
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation customerCreate($input: CustomerInput!) {
    customerCreate(input: $input) {
      userErrors {
        field
        message
      }
      customer {
        id
        email
        phone
        taxExempt
        firstName
        lastName
        amountSpent {
          amount
          currencyCode
        }
        smsMarketingConsent {
          marketingState
          marketingOptInLevel
          consentUpdatedAt
        }
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "email": "steve.lastnameson@example.com",
      "phone": "+16465555555",
      "firstName": "Steve",
      "smsMarketingConsent": {
        "marketingState": "SUBSCRIBED",
        "marketingOptInLevel": "SINGLE_OPT_IN"
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "customerCreate": {
      "userErrors": [],
      "customer": {
        "id": "gid://shopify/Customer/1073340122",
        "email": "steve.lastnameson@example.com",
        "phone": "+16465555555",
        "taxExempt": false,
        "firstName": "Steve",
        "lastName": null,
        "amountSpent": {
          "amount": "0.0",
          "currencyCode": "USD"
        },
        "smsMarketingConsent": {
          "marketingState": "SUBSCRIBED",
          "marketingOptInLevel": "SINGLE_OPT_IN",
          "consentUpdatedAt": "2024-11-05T14:29:24Z"
        }
      }
    }
  }
  ```

* ### Create a customer without required attributes

  #### Description

  Creating a customer without an email, phone, first name or last name fails and returns an error.

  #### Query

  ```graphql
  mutation customerCreate($input: CustomerInput!) {
    customerCreate(input: $input) {
      userErrors {
        field
        message
      }
      customer {
        id
        email
        phone
        taxExempt
        emailMarketingConsent {
          marketingState
          marketingOptInLevel
          consentUpdatedAt
        }
        firstName
        lastName
        amountSpent {
          amount
          currencyCode
        }
        smsMarketingConsent {
          marketingState
          marketingOptInLevel
        }
        addresses {
          address1
          city
          countryCode
          phone
          zip
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "email": null,
      "phone": null,
      "firstName": null,
      "lastName": null
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
  "query": "mutation customerCreate($input: CustomerInput!) { customerCreate(input: $input) { userErrors { field message } customer { id email phone taxExempt emailMarketingConsent { marketingState marketingOptInLevel consentUpdatedAt } firstName lastName amountSpent { amount currencyCode } smsMarketingConsent { marketingState marketingOptInLevel } addresses { address1 city countryCode phone zip } } } }",
   "variables": {
      "input": {
        "email": null,
        "phone": null,
        "firstName": null,
        "lastName": null
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
    mutation customerCreate($input: CustomerInput!) {
      customerCreate(input: $input) {
        userErrors {
          field
          message
        }
        customer {
          id
          email
          phone
          taxExempt
          emailMarketingConsent {
            marketingState
            marketingOptInLevel
            consentUpdatedAt
          }
          firstName
          lastName
          amountSpent {
            amount
            currencyCode
          }
          smsMarketingConsent {
            marketingState
            marketingOptInLevel
          }
          addresses {
            address1
            city
            countryCode
            phone
            zip
          }
        }
      }
    }`,
    {
      variables: {
          "input": {
              "email": null,
              "phone": null,
              "firstName": null,
              "lastName": null
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
    mutation customerCreate($input: CustomerInput!) {
      customerCreate(input: $input) {
        userErrors {
          field
          message
        }
        customer {
          id
          email
          phone
          taxExempt
          emailMarketingConsent {
            marketingState
            marketingOptInLevel
            consentUpdatedAt
          }
          firstName
          lastName
          amountSpent {
            amount
            currencyCode
          }
          smsMarketingConsent {
            marketingState
            marketingOptInLevel
          }
          addresses {
            address1
            city
            countryCode
            phone
            zip
          }
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "email": null,
      "phone": null,
      "firstName": null,
      "lastName": null
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation customerCreate($input: CustomerInput!) {
        customerCreate(input: $input) {
          userErrors {
            field
            message
          }
          customer {
            id
            email
            phone
            taxExempt
            emailMarketingConsent {
              marketingState
              marketingOptInLevel
              consentUpdatedAt
            }
            firstName
            lastName
            amountSpent {
              amount
              currencyCode
            }
            smsMarketingConsent {
              marketingState
              marketingOptInLevel
            }
            addresses {
              address1
              city
              countryCode
              phone
              zip
            }
          }
        }
      }`,
      "variables": {
          "input": {
              "email": null,
              "phone": null,
              "firstName": null,
              "lastName": null
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation customerCreate($input: CustomerInput!) {
    customerCreate(input: $input) {
      userErrors {
        field
        message
      }
      customer {
        id
        email
        phone
        taxExempt
        emailMarketingConsent {
          marketingState
          marketingOptInLevel
          consentUpdatedAt
        }
        firstName
        lastName
        amountSpent {
          amount
          currencyCode
        }
        smsMarketingConsent {
          marketingState
          marketingOptInLevel
        }
        addresses {
          address1
          city
          countryCode
          phone
          zip
        }
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "email": null,
      "phone": null,
      "firstName": null,
      "lastName": null
    }
  }'
  ```

  #### Response

  ```json
  {
    "customerCreate": {
      "userErrors": [
        {
          "field": null,
          "message": "Customer must have a name, phone number or email address"
        }
      ],
      "customer": null
    }
  }
  ```

* ### Create a new metafield on a new customer

  #### Description

  Create a new metafield \`my\_field.nickname\` on a new customer. Alternatively, refer to the \[metafieldsSet]\(https://shopify.dev/api/admin-graphql/latest/mutations/metafieldsset) mutation to create and/or update metafields on customer resources.

  #### Query

  ```graphql
  mutation createCustomerMetafields($input: CustomerInput!) {
    customerCreate(input: $input) {
      customer {
        id
        metafields(first: 3) {
          edges {
            node {
              id
              namespace
              key
              value
            }
          }
        }
      }
      userErrors {
        message
        field
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "metafields": [
        {
          "namespace": "my_field",
          "key": "nickname",
          "type": "single_line_text_field",
          "value": "rob"
        }
      ],
      "email": "bob.norman@example.com"
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
  "query": "mutation createCustomerMetafields($input: CustomerInput!) { customerCreate(input: $input) { customer { id metafields(first: 3) { edges { node { id namespace key value } } } } userErrors { message field } } }",
   "variables": {
      "input": {
        "metafields": [
          {
            "namespace": "my_field",
            "key": "nickname",
            "type": "single_line_text_field",
            "value": "rob"
          }
        ],
        "email": "bob.norman@example.com"
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
    mutation createCustomerMetafields($input: CustomerInput!) {
      customerCreate(input: $input) {
        customer {
          id
          metafields(first: 3) {
            edges {
              node {
                id
                namespace
                key
                value
              }
            }
          }
        }
        userErrors {
          message
          field
        }
      }
    }`,
    {
      variables: {
          "input": {
              "metafields": [
                  {
                      "namespace": "my_field",
                      "key": "nickname",
                      "type": "single_line_text_field",
                      "value": "rob"
                  }
              ],
              "email": "bob.norman@example.com"
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
    mutation createCustomerMetafields($input: CustomerInput!) {
      customerCreate(input: $input) {
        customer {
          id
          metafields(first: 3) {
            edges {
              node {
                id
                namespace
                key
                value
              }
            }
          }
        }
        userErrors {
          message
          field
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "metafields": [
        {
          "namespace": "my_field",
          "key": "nickname",
          "type": "single_line_text_field",
          "value": "rob"
        }
      ],
      "email": "bob.norman@example.com"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation createCustomerMetafields($input: CustomerInput!) {
        customerCreate(input: $input) {
          customer {
            id
            metafields(first: 3) {
              edges {
                node {
                  id
                  namespace
                  key
                  value
                }
              }
            }
          }
          userErrors {
            message
            field
          }
        }
      }`,
      "variables": {
          "input": {
              "metafields": [
                  {
                      "namespace": "my_field",
                      "key": "nickname",
                      "type": "single_line_text_field",
                      "value": "rob"
                  }
              ],
              "email": "bob.norman@example.com"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation createCustomerMetafields($input: CustomerInput!) {
    customerCreate(input: $input) {
      customer {
        id
        metafields(first: 3) {
          edges {
            node {
              id
              namespace
              key
              value
            }
          }
        }
      }
      userErrors {
        message
        field
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "metafields": [
        {
          "namespace": "my_field",
          "key": "nickname",
          "type": "single_line_text_field",
          "value": "rob"
        }
      ],
      "email": "bob.norman@example.com"
    }
  }'
  ```

  #### Response

  ```json
  {
    "customerCreate": {
      "customer": {
        "id": "gid://shopify/Customer/1073340085",
        "metafields": {
          "edges": [
            {
              "node": {
                "id": "gid://shopify/Metafield/1069230109",
                "namespace": "my_field",
                "key": "nickname",
                "value": "rob"
              }
            }
          ]
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Creates a customer

  #### Description

  Create a customer with an address.

  #### Query

  ```graphql
  mutation customerCreate($input: CustomerInput!) {
    customerCreate(input: $input) {
      userErrors {
        field
        message
      }
      customer {
        id
        email
        phone
        taxExempt
        emailMarketingConsent {
          marketingState
          marketingOptInLevel
          consentUpdatedAt
        }
        firstName
        lastName
        amountSpent {
          amount
          currencyCode
        }
        smsMarketingConsent {
          marketingState
          marketingOptInLevel
        }
        addresses {
          address1
          city
          country
          phone
          zip
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "email": "steve.lastnameson@example.com",
      "phone": "+16465555555",
      "firstName": "Steve",
      "lastName": "Lastname",
      "emailMarketingConsent": {
        "marketingOptInLevel": "CONFIRMED_OPT_IN",
        "marketingState": "SUBSCRIBED"
      },
      "addresses": [
        {
          "address1": "412 fake st",
          "city": "Ottawa",
          "province": "ON",
          "phone": "+16469999999",
          "zip": "A1A 4A1",
          "lastName": "Lastname",
          "firstName": "Steve",
          "countryCode": "CA"
        }
      ]
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
  "query": "mutation customerCreate($input: CustomerInput!) { customerCreate(input: $input) { userErrors { field message } customer { id email phone taxExempt emailMarketingConsent { marketingState marketingOptInLevel consentUpdatedAt } firstName lastName amountSpent { amount currencyCode } smsMarketingConsent { marketingState marketingOptInLevel } addresses { address1 city country phone zip } } } }",
   "variables": {
      "input": {
        "email": "steve.lastnameson@example.com",
        "phone": "+16465555555",
        "firstName": "Steve",
        "lastName": "Lastname",
        "emailMarketingConsent": {
          "marketingOptInLevel": "CONFIRMED_OPT_IN",
          "marketingState": "SUBSCRIBED"
        },
        "addresses": [
          {
            "address1": "412 fake st",
            "city": "Ottawa",
            "province": "ON",
            "phone": "+16469999999",
            "zip": "A1A 4A1",
            "lastName": "Lastname",
            "firstName": "Steve",
            "countryCode": "CA"
          }
        ]
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
    mutation customerCreate($input: CustomerInput!) {
      customerCreate(input: $input) {
        userErrors {
          field
          message
        }
        customer {
          id
          email
          phone
          taxExempt
          emailMarketingConsent {
            marketingState
            marketingOptInLevel
            consentUpdatedAt
          }
          firstName
          lastName
          amountSpent {
            amount
            currencyCode
          }
          smsMarketingConsent {
            marketingState
            marketingOptInLevel
          }
          addresses {
            address1
            city
            country
            phone
            zip
          }
        }
      }
    }`,
    {
      variables: {
          "input": {
              "email": "steve.lastnameson@example.com",
              "phone": "+16465555555",
              "firstName": "Steve",
              "lastName": "Lastname",
              "emailMarketingConsent": {
                  "marketingOptInLevel": "CONFIRMED_OPT_IN",
                  "marketingState": "SUBSCRIBED"
              },
              "addresses": [
                  {
                      "address1": "412 fake st",
                      "city": "Ottawa",
                      "province": "ON",
                      "phone": "+16469999999",
                      "zip": "A1A 4A1",
                      "lastName": "Lastname",
                      "firstName": "Steve",
                      "countryCode": "CA"
                  }
              ]
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
    mutation customerCreate($input: CustomerInput!) {
      customerCreate(input: $input) {
        userErrors {
          field
          message
        }
        customer {
          id
          email
          phone
          taxExempt
          emailMarketingConsent {
            marketingState
            marketingOptInLevel
            consentUpdatedAt
          }
          firstName
          lastName
          amountSpent {
            amount
            currencyCode
          }
          smsMarketingConsent {
            marketingState
            marketingOptInLevel
          }
          addresses {
            address1
            city
            country
            phone
            zip
          }
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "email": "steve.lastnameson@example.com",
      "phone": "+16465555555",
      "firstName": "Steve",
      "lastName": "Lastname",
      "emailMarketingConsent": {
        "marketingOptInLevel": "CONFIRMED_OPT_IN",
        "marketingState": "SUBSCRIBED"
      },
      "addresses": [
        {
          "address1": "412 fake st",
          "city": "Ottawa",
          "province": "ON",
          "phone": "+16469999999",
          "zip": "A1A 4A1",
          "lastName": "Lastname",
          "firstName": "Steve",
          "countryCode": "CA"
        }
      ]
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation customerCreate($input: CustomerInput!) {
        customerCreate(input: $input) {
          userErrors {
            field
            message
          }
          customer {
            id
            email
            phone
            taxExempt
            emailMarketingConsent {
              marketingState
              marketingOptInLevel
              consentUpdatedAt
            }
            firstName
            lastName
            amountSpent {
              amount
              currencyCode
            }
            smsMarketingConsent {
              marketingState
              marketingOptInLevel
            }
            addresses {
              address1
              city
              country
              phone
              zip
            }
          }
        }
      }`,
      "variables": {
          "input": {
              "email": "steve.lastnameson@example.com",
              "phone": "+16465555555",
              "firstName": "Steve",
              "lastName": "Lastname",
              "emailMarketingConsent": {
                  "marketingOptInLevel": "CONFIRMED_OPT_IN",
                  "marketingState": "SUBSCRIBED"
              },
              "addresses": [
                  {
                      "address1": "412 fake st",
                      "city": "Ottawa",
                      "province": "ON",
                      "phone": "+16469999999",
                      "zip": "A1A 4A1",
                      "lastName": "Lastname",
                      "firstName": "Steve",
                      "countryCode": "CA"
                  }
              ]
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation customerCreate($input: CustomerInput!) {
    customerCreate(input: $input) {
      userErrors {
        field
        message
      }
      customer {
        id
        email
        phone
        taxExempt
        emailMarketingConsent {
          marketingState
          marketingOptInLevel
          consentUpdatedAt
        }
        firstName
        lastName
        amountSpent {
          amount
          currencyCode
        }
        smsMarketingConsent {
          marketingState
          marketingOptInLevel
        }
        addresses {
          address1
          city
          country
          phone
          zip
        }
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "email": "steve.lastnameson@example.com",
      "phone": "+16465555555",
      "firstName": "Steve",
      "lastName": "Lastname",
      "emailMarketingConsent": {
        "marketingOptInLevel": "CONFIRMED_OPT_IN",
        "marketingState": "SUBSCRIBED"
      },
      "addresses": [
        {
          "address1": "412 fake st",
          "city": "Ottawa",
          "province": "ON",
          "phone": "+16469999999",
          "zip": "A1A 4A1",
          "lastName": "Lastname",
          "firstName": "Steve",
          "countryCode": "CA"
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "customerCreate": {
      "userErrors": [],
      "customer": {
        "id": "gid://shopify/Customer/1073340090",
        "email": "steve.lastnameson@example.com",
        "phone": "+16465555555",
        "taxExempt": false,
        "emailMarketingConsent": {
          "marketingState": "SUBSCRIBED",
          "marketingOptInLevel": "CONFIRMED_OPT_IN",
          "consentUpdatedAt": "2024-11-05T14:29:06Z"
        },
        "firstName": "Steve",
        "lastName": "Lastname",
        "amountSpent": {
          "amount": "0.0",
          "currencyCode": "USD"
        },
        "smsMarketingConsent": {
          "marketingState": "NOT_SUBSCRIBED",
          "marketingOptInLevel": "SINGLE_OPT_IN"
        },
        "addresses": [
          {
            "address1": "412 fake st",
            "city": "Ottawa",
            "country": "Canada",
            "phone": "+16469999999",
            "zip": "A1A 4A1"
          }
        ]
      }
    }
  }
  ```

* ### customerCreate reference
