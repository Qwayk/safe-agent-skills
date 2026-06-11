---
title: customerSendAccountInviteEmail - GraphQL Admin
description: >-
  Sends an email invitation for a customer to create a legacy customer account.
  The invitation lets customers set up their password and activate their account
  in the online store.


  You can optionally customize the email content including the subject, sender,
  recipients, and message body. If you don't provide email customization, the
  store uses its default account invitation template.


  > Note: The invite only works when legacy customer accounts are enabled on the
  shop.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerSendAccountInviteEmail
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerSendAccountInviteEmail.md
---

# customer​Send​Account​Invite​Email

mutation

Requires `write_customers` access scope. Also: The user must have permission to create and edit customers.

Sends an email invitation for a customer to create a legacy customer account. The invitation lets customers set up their password and activate their account in the online store.

You can optionally customize the email content including the subject, sender, recipients, and message body. If you don't provide email customization, the store uses its default account invitation template.

***

**Note:** The invite only works when legacy customer accounts are enabled on the shop.

***

## Arguments

* customer​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the customer to whom an account invite email is to be sent.

* email

  [Email​Input](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/EmailInput)

  Specifies the account invite email fields.

***

## Customer​Send​Account​Invite​Email​Payload returns

* customer

  [Customer](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)

  The customer to whom an account invite email was sent.

* user​Errors

  [\[Customer​Send​Account​Invite​Email​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CustomerSendAccountInviteEmailUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Sends an account invite to a customer

  #### Query

  ```graphql
  mutation CustomerSendAccountInviteEmail($customerId: ID!) {
    customerSendAccountInviteEmail(customerId: $customerId) {
      customer {
        id
      }
      userErrors {
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "customerId": "gid://shopify/Customer/105906728"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation CustomerSendAccountInviteEmail($customerId: ID!) { customerSendAccountInviteEmail(customerId: $customerId) { customer { id } userErrors { field message } } }",
   "variables": {
      "customerId": "gid://shopify/Customer/105906728"
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
    mutation CustomerSendAccountInviteEmail($customerId: ID!) {
      customerSendAccountInviteEmail(customerId: $customerId) {
        customer {
          id
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "customerId": "gid://shopify/Customer/105906728"
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
    mutation CustomerSendAccountInviteEmail($customerId: ID!) {
      customerSendAccountInviteEmail(customerId: $customerId) {
        customer {
          id
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "customerId": "gid://shopify/Customer/105906728"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation CustomerSendAccountInviteEmail($customerId: ID!) {
        customerSendAccountInviteEmail(customerId: $customerId) {
          customer {
            id
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "customerId": "gid://shopify/Customer/105906728"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation CustomerSendAccountInviteEmail($customerId: ID!) {
    customerSendAccountInviteEmail(customerId: $customerId) {
      customer {
        id
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "customerId": "gid://shopify/Customer/105906728"
  }'
  ```

  #### Response

  ```json
  {
    "customerSendAccountInviteEmail": {
      "customer": {
        "id": "gid://shopify/Customer/105906728"
      },
      "userErrors": []
    }
  }
  ```

* ### customerSendAccountInviteEmail reference
