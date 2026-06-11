---
title: customerSmsMarketingConsentUpdate - GraphQL Admin
description: >-
  Updates a
  [customer](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)'s
  SMS marketing consent information. The customer must have a phone number on
  their account to receive SMS marketing.


  You can set whether the customer subscribes or unsubscribes to SMS marketing
  and specify the [opt-in
  level](https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerSmsMarketingConsentUpdate#arguments-input.fields.smsMarketingConsent.marketingOptInLevel).
  Optionally include when the consent was collected and which
  [location](https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerSmsMarketingConsentUpdate#arguments-input.fields.smsMarketingConsent.sourceLocationId)
  collected it.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerSmsMarketingConsentUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerSmsMarketingConsentUpdate.md
---

# customer​Sms​Marketing​Consent​Update

mutation

Requires `write_customers` access scope.

Updates a [customer](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)'s SMS marketing consent information. The customer must have a phone number on their account to receive SMS marketing.

You can set whether the customer subscribes or unsubscribes to SMS marketing and specify the [opt-in level](https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerSmsMarketingConsentUpdate#arguments-input.fields.smsMarketingConsent.marketingOptInLevel). Optionally include when the consent was collected and which [location](https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerSmsMarketingConsentUpdate#arguments-input.fields.smsMarketingConsent.sourceLocationId) collected it.

## Arguments

* input

  [Customer​Sms​Marketing​Consent​Update​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CustomerSmsMarketingConsentUpdateInput)

  required

  Specifies the input fields to update a customer's SMS marketing consent information.

***

## Customer​Sms​Marketing​Consent​Update​Payload returns

* customer

  [Customer](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)

  The updated customer.

* user​Errors

  [\[Customer​Sms​Marketing​Consent​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CustomerSmsMarketingConsentError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Subscribe a customer to SMS marketing materials

  #### Query

  ```graphql
  mutation customerSmsMarketingConsentUpdate($input: CustomerSmsMarketingConsentUpdateInput!) {
    customerSmsMarketingConsentUpdate(input: $input) {
      userErrors {
        field
        message
      }
      customer {
        id
        phone
        smsMarketingConsent {
          marketingState
          marketingOptInLevel
          consentUpdatedAt
          consentCollectedFrom
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "customerId": "gid://shopify/Customer/207119551",
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
  "query": "mutation customerSmsMarketingConsentUpdate($input: CustomerSmsMarketingConsentUpdateInput!) { customerSmsMarketingConsentUpdate(input: $input) { userErrors { field message } customer { id phone smsMarketingConsent { marketingState marketingOptInLevel consentUpdatedAt consentCollectedFrom } } } }",
   "variables": {
      "input": {
        "customerId": "gid://shopify/Customer/207119551",
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
    mutation customerSmsMarketingConsentUpdate($input: CustomerSmsMarketingConsentUpdateInput!) {
      customerSmsMarketingConsentUpdate(input: $input) {
        userErrors {
          field
          message
        }
        customer {
          id
          phone
          smsMarketingConsent {
            marketingState
            marketingOptInLevel
            consentUpdatedAt
            consentCollectedFrom
          }
        }
      }
    }`,
    {
      variables: {
          "input": {
              "customerId": "gid://shopify/Customer/207119551",
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
    mutation customerSmsMarketingConsentUpdate($input: CustomerSmsMarketingConsentUpdateInput!) {
      customerSmsMarketingConsentUpdate(input: $input) {
        userErrors {
          field
          message
        }
        customer {
          id
          phone
          smsMarketingConsent {
            marketingState
            marketingOptInLevel
            consentUpdatedAt
            consentCollectedFrom
          }
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "customerId": "gid://shopify/Customer/207119551",
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
      "query": `mutation customerSmsMarketingConsentUpdate($input: CustomerSmsMarketingConsentUpdateInput!) {
        customerSmsMarketingConsentUpdate(input: $input) {
          userErrors {
            field
            message
          }
          customer {
            id
            phone
            smsMarketingConsent {
              marketingState
              marketingOptInLevel
              consentUpdatedAt
              consentCollectedFrom
            }
          }
        }
      }`,
      "variables": {
          "input": {
              "customerId": "gid://shopify/Customer/207119551",
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
  'mutation customerSmsMarketingConsentUpdate($input: CustomerSmsMarketingConsentUpdateInput!) {
    customerSmsMarketingConsentUpdate(input: $input) {
      userErrors {
        field
        message
      }
      customer {
        id
        phone
        smsMarketingConsent {
          marketingState
          marketingOptInLevel
          consentUpdatedAt
          consentCollectedFrom
        }
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "customerId": "gid://shopify/Customer/207119551",
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
    "customerSmsMarketingConsentUpdate": {
      "userErrors": [],
      "customer": {
        "id": "gid://shopify/Customer/207119551",
        "phone": "+16136120707",
        "smsMarketingConsent": {
          "marketingState": "SUBSCRIBED",
          "marketingOptInLevel": "SINGLE_OPT_IN",
          "consentUpdatedAt": "2024-09-12T01:08:05Z",
          "consentCollectedFrom": "OTHER"
        }
      }
    }
  }
  ```

* ### Subscribe a customer to SMS marketing materials with the date at which the consent was collected

  #### Query

  ```graphql
  mutation customerSmsMarketingConsentUpdate($input: CustomerSmsMarketingConsentUpdateInput!) {
    customerSmsMarketingConsentUpdate(input: $input) {
      userErrors {
        field
        message
      }
      customer {
        id
        phone
        smsMarketingConsent {
          marketingState
          marketingOptInLevel
          consentUpdatedAt
          consentCollectedFrom
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "customerId": "gid://shopify/Customer/207119551",
      "smsMarketingConsent": {
        "marketingState": "UNSUBSCRIBED",
        "marketingOptInLevel": "SINGLE_OPT_IN",
        "consentUpdatedAt": "2021-01-07T15:50:00Z"
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
  "query": "mutation customerSmsMarketingConsentUpdate($input: CustomerSmsMarketingConsentUpdateInput!) { customerSmsMarketingConsentUpdate(input: $input) { userErrors { field message } customer { id phone smsMarketingConsent { marketingState marketingOptInLevel consentUpdatedAt consentCollectedFrom } } } }",
   "variables": {
      "input": {
        "customerId": "gid://shopify/Customer/207119551",
        "smsMarketingConsent": {
          "marketingState": "UNSUBSCRIBED",
          "marketingOptInLevel": "SINGLE_OPT_IN",
          "consentUpdatedAt": "2021-01-07T15:50:00Z"
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
    mutation customerSmsMarketingConsentUpdate($input: CustomerSmsMarketingConsentUpdateInput!) {
      customerSmsMarketingConsentUpdate(input: $input) {
        userErrors {
          field
          message
        }
        customer {
          id
          phone
          smsMarketingConsent {
            marketingState
            marketingOptInLevel
            consentUpdatedAt
            consentCollectedFrom
          }
        }
      }
    }`,
    {
      variables: {
          "input": {
              "customerId": "gid://shopify/Customer/207119551",
              "smsMarketingConsent": {
                  "marketingState": "UNSUBSCRIBED",
                  "marketingOptInLevel": "SINGLE_OPT_IN",
                  "consentUpdatedAt": "2021-01-07T15:50:00Z"
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
    mutation customerSmsMarketingConsentUpdate($input: CustomerSmsMarketingConsentUpdateInput!) {
      customerSmsMarketingConsentUpdate(input: $input) {
        userErrors {
          field
          message
        }
        customer {
          id
          phone
          smsMarketingConsent {
            marketingState
            marketingOptInLevel
            consentUpdatedAt
            consentCollectedFrom
          }
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "customerId": "gid://shopify/Customer/207119551",
      "smsMarketingConsent": {
        "marketingState": "UNSUBSCRIBED",
        "marketingOptInLevel": "SINGLE_OPT_IN",
        "consentUpdatedAt": "2021-01-07T15:50:00Z"
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
      "query": `mutation customerSmsMarketingConsentUpdate($input: CustomerSmsMarketingConsentUpdateInput!) {
        customerSmsMarketingConsentUpdate(input: $input) {
          userErrors {
            field
            message
          }
          customer {
            id
            phone
            smsMarketingConsent {
              marketingState
              marketingOptInLevel
              consentUpdatedAt
              consentCollectedFrom
            }
          }
        }
      }`,
      "variables": {
          "input": {
              "customerId": "gid://shopify/Customer/207119551",
              "smsMarketingConsent": {
                  "marketingState": "UNSUBSCRIBED",
                  "marketingOptInLevel": "SINGLE_OPT_IN",
                  "consentUpdatedAt": "2021-01-07T15:50:00Z"
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
  'mutation customerSmsMarketingConsentUpdate($input: CustomerSmsMarketingConsentUpdateInput!) {
    customerSmsMarketingConsentUpdate(input: $input) {
      userErrors {
        field
        message
      }
      customer {
        id
        phone
        smsMarketingConsent {
          marketingState
          marketingOptInLevel
          consentUpdatedAt
          consentCollectedFrom
        }
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "customerId": "gid://shopify/Customer/207119551",
      "smsMarketingConsent": {
        "marketingState": "UNSUBSCRIBED",
        "marketingOptInLevel": "SINGLE_OPT_IN",
        "consentUpdatedAt": "2021-01-07T15:50:00Z"
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "customerSmsMarketingConsentUpdate": {
      "userErrors": [],
      "customer": {
        "id": "gid://shopify/Customer/207119551",
        "phone": "+16136120707",
        "smsMarketingConsent": {
          "marketingState": "UNSUBSCRIBED",
          "marketingOptInLevel": "SINGLE_OPT_IN",
          "consentUpdatedAt": "2021-01-07T15:50:00Z",
          "consentCollectedFrom": "OTHER"
        }
      }
    }
  }
  ```

* ### Unsubscribe a customer from SMS marketing materials

  #### Query

  ```graphql
  mutation customerSmsMarketingConsentUpdate($input: CustomerSmsMarketingConsentUpdateInput!) {
    customerSmsMarketingConsentUpdate(input: $input) {
      userErrors {
        field
        message
      }
      customer {
        id
        phone
        smsMarketingConsent {
          marketingState
          marketingOptInLevel
          consentUpdatedAt
          consentCollectedFrom
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "customerId": "gid://shopify/Customer/207119551",
      "smsMarketingConsent": {
        "marketingState": "UNSUBSCRIBED",
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
  "query": "mutation customerSmsMarketingConsentUpdate($input: CustomerSmsMarketingConsentUpdateInput!) { customerSmsMarketingConsentUpdate(input: $input) { userErrors { field message } customer { id phone smsMarketingConsent { marketingState marketingOptInLevel consentUpdatedAt consentCollectedFrom } } } }",
   "variables": {
      "input": {
        "customerId": "gid://shopify/Customer/207119551",
        "smsMarketingConsent": {
          "marketingState": "UNSUBSCRIBED",
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
    mutation customerSmsMarketingConsentUpdate($input: CustomerSmsMarketingConsentUpdateInput!) {
      customerSmsMarketingConsentUpdate(input: $input) {
        userErrors {
          field
          message
        }
        customer {
          id
          phone
          smsMarketingConsent {
            marketingState
            marketingOptInLevel
            consentUpdatedAt
            consentCollectedFrom
          }
        }
      }
    }`,
    {
      variables: {
          "input": {
              "customerId": "gid://shopify/Customer/207119551",
              "smsMarketingConsent": {
                  "marketingState": "UNSUBSCRIBED",
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
    mutation customerSmsMarketingConsentUpdate($input: CustomerSmsMarketingConsentUpdateInput!) {
      customerSmsMarketingConsentUpdate(input: $input) {
        userErrors {
          field
          message
        }
        customer {
          id
          phone
          smsMarketingConsent {
            marketingState
            marketingOptInLevel
            consentUpdatedAt
            consentCollectedFrom
          }
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "customerId": "gid://shopify/Customer/207119551",
      "smsMarketingConsent": {
        "marketingState": "UNSUBSCRIBED",
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
      "query": `mutation customerSmsMarketingConsentUpdate($input: CustomerSmsMarketingConsentUpdateInput!) {
        customerSmsMarketingConsentUpdate(input: $input) {
          userErrors {
            field
            message
          }
          customer {
            id
            phone
            smsMarketingConsent {
              marketingState
              marketingOptInLevel
              consentUpdatedAt
              consentCollectedFrom
            }
          }
        }
      }`,
      "variables": {
          "input": {
              "customerId": "gid://shopify/Customer/207119551",
              "smsMarketingConsent": {
                  "marketingState": "UNSUBSCRIBED",
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
  'mutation customerSmsMarketingConsentUpdate($input: CustomerSmsMarketingConsentUpdateInput!) {
    customerSmsMarketingConsentUpdate(input: $input) {
      userErrors {
        field
        message
      }
      customer {
        id
        phone
        smsMarketingConsent {
          marketingState
          marketingOptInLevel
          consentUpdatedAt
          consentCollectedFrom
        }
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "customerId": "gid://shopify/Customer/207119551",
      "smsMarketingConsent": {
        "marketingState": "UNSUBSCRIBED",
        "marketingOptInLevel": "SINGLE_OPT_IN"
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "customerSmsMarketingConsentUpdate": {
      "userErrors": [],
      "customer": {
        "id": "gid://shopify/Customer/207119551",
        "phone": "+16136120707",
        "smsMarketingConsent": {
          "marketingState": "UNSUBSCRIBED",
          "marketingOptInLevel": "SINGLE_OPT_IN",
          "consentUpdatedAt": "2024-09-12T01:08:05Z",
          "consentCollectedFrom": "OTHER"
        }
      }
    }
  }
  ```

* ### customerSmsMarketingConsentUpdate reference
