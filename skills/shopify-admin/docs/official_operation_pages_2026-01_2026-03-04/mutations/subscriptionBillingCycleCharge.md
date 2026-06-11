---
title: subscriptionBillingCycleCharge - GraphQL Admin
description: >-
  Creates a new subscription billing attempt for a specified billing cycle. This
  is the alternative mutation for
  [subscriptionBillingAttemptCreate](https://shopify.dev/docs/api/admin-graphql/latest/mutations/subscriptionBillingAttemptCreate).
  For more information, refer to [Create a subscription
  contract](https://shopify.dev/docs/apps/selling-strategies/subscriptions/contracts/create#step-4-create-a-billing-attempt).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/subscriptionBillingCycleCharge
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/subscriptionBillingCycleCharge.md
---

# subscription​Billing​Cycle​Charge

mutation

Requires `write_own_subscription_contracts` access scope. Also: The user must have manage\_orders\_information permission.

Creates a new subscription billing attempt for a specified billing cycle. This is the alternative mutation for [subscriptionBillingAttemptCreate](https://shopify.dev/docs/api/admin-graphql/latest/mutations/subscriptionBillingAttemptCreate). For more information, refer to [Create a subscription contract](https://shopify.dev/docs/apps/selling-strategies/subscriptions/contracts/create#step-4-create-a-billing-attempt).

## Arguments

* billing​Cycle​Selector

  [Subscription​Billing​Cycle​Selector!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/SubscriptionBillingCycleSelector)

  required

  Select the specific billing cycle to be billed. If the selected billing cycle's [billingAttemptExpectedDate](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionBillingCycle#field-subscriptionbillingcycle-billingattemptexpecteddate) is in the past, the [originTime](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionBillingAttempt#field-subscriptionbillingattempt-origintime) of the billing attempt will be set to this date. However, if the [billingAttemptExpectedDate](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionBillingCycle#field-subscriptionbillingcycle-billingattemptexpecteddate) is in the future, the originTime will be the current time.

* inventory​Policy

  [Subscription​Billing​Attempt​Inventory​Policy](https://shopify.dev/docs/api/admin-graphql/latest/enums/SubscriptionBillingAttemptInventoryPolicy)

  Default:PRODUCT\_VARIANT\_INVENTORY\_POLICY

  The behaviour to use when updating inventory.

* subscription​Contract​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the subscription contract.

***

## Subscription​Billing​Cycle​Charge​Payload returns

* subscription​Billing​Attempt

  [Subscription​Billing​Attempt](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionBillingAttempt)

  The subscription billing attempt.

* user​Errors

  [\[Billing​Attempt​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/BillingAttemptUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a billing attempt on a specific billing cycle

  #### Description

  Creates a billing attempt on the billing cycle with date \`2023-01-05T12:00:00Z\`.

  #### Query

  ```graphql
  mutation subscriptionBillingCycleCharge($contractId: ID!, $billingCycleSelector: SubscriptionBillingCycleSelector!) {
    subscriptionBillingCycleCharge(subscriptionContractId: $contractId, billingCycleSelector: $billingCycleSelector) {
      subscriptionBillingAttempt {
        id
        ready
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
    "contractId": "gid://shopify/SubscriptionContract/593791907",
    "billingCycleSelector": {
      "date": "2023-01-05T12:00:00Z"
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
  "query": "mutation subscriptionBillingCycleCharge($contractId: ID!, $billingCycleSelector: SubscriptionBillingCycleSelector!) { subscriptionBillingCycleCharge(subscriptionContractId: $contractId, billingCycleSelector: $billingCycleSelector) { subscriptionBillingAttempt { id ready } userErrors { field message } } }",
   "variables": {
      "contractId": "gid://shopify/SubscriptionContract/593791907",
      "billingCycleSelector": {
        "date": "2023-01-05T12:00:00Z"
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
    mutation subscriptionBillingCycleCharge($contractId: ID!, $billingCycleSelector: SubscriptionBillingCycleSelector!) {
      subscriptionBillingCycleCharge(subscriptionContractId: $contractId, billingCycleSelector: $billingCycleSelector) {
        subscriptionBillingAttempt {
          id
          ready
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "contractId": "gid://shopify/SubscriptionContract/593791907",
          "billingCycleSelector": {
              "date": "2023-01-05T12:00:00Z"
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
    mutation subscriptionBillingCycleCharge($contractId: ID!, $billingCycleSelector: SubscriptionBillingCycleSelector!) {
      subscriptionBillingCycleCharge(subscriptionContractId: $contractId, billingCycleSelector: $billingCycleSelector) {
        subscriptionBillingAttempt {
          id
          ready
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "contractId": "gid://shopify/SubscriptionContract/593791907",
    "billingCycleSelector": {
      "date": "2023-01-05T12:00:00Z"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation subscriptionBillingCycleCharge($contractId: ID!, $billingCycleSelector: SubscriptionBillingCycleSelector!) {
        subscriptionBillingCycleCharge(subscriptionContractId: $contractId, billingCycleSelector: $billingCycleSelector) {
          subscriptionBillingAttempt {
            id
            ready
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "contractId": "gid://shopify/SubscriptionContract/593791907",
          "billingCycleSelector": {
              "date": "2023-01-05T12:00:00Z"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation subscriptionBillingCycleCharge($contractId: ID!, $billingCycleSelector: SubscriptionBillingCycleSelector!) {
    subscriptionBillingCycleCharge(subscriptionContractId: $contractId, billingCycleSelector: $billingCycleSelector) {
      subscriptionBillingAttempt {
        id
        ready
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "contractId": "gid://shopify/SubscriptionContract/593791907",
    "billingCycleSelector": {
      "date": "2023-01-05T12:00:00Z"
    }
  }'
  ```

  #### Response

  ```json
  {
    "subscriptionBillingCycleCharge": {
      "subscriptionBillingAttempt": {
        "id": "gid://shopify/SubscriptionBillingAttempt/528177098",
        "ready": false
      },
      "userErrors": []
    }
  }
  ```

* ### subscriptionBillingCycleCharge reference
