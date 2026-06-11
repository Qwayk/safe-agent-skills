---
title: subscriptionBillingCycleScheduleEdit - GraphQL Admin
description: Modify the schedule of a specific billing cycle.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/subscriptionBillingCycleScheduleEdit
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/subscriptionBillingCycleScheduleEdit.md
---

# subscription​Billing​Cycle​Schedule​Edit

mutation

Requires `write_own_subscription_contracts` access scope. Also: The user must have manage\_orders\_information permission.

Modify the schedule of a specific billing cycle.

## Arguments

* billing​Cycle​Input

  [Subscription​Billing​Cycle​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/SubscriptionBillingCycleInput)

  required

  Input object for selecting and using billing cycles.

* input

  [Subscription​Billing​Cycle​Schedule​Edit​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/SubscriptionBillingCycleScheduleEditInput)

  required

  Data used to create or modify billing cycle schedule edit.

***

## Subscription​Billing​Cycle​Schedule​Edit​Payload returns

* billing​Cycle

  [Subscription​Billing​Cycle](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionBillingCycle)

  The updated billing cycle.

* user​Errors

  [\[Subscription​Billing​Cycle​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionBillingCycleUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Change the billing date of a cycle

  #### Description

  Changes the \`billingAttemptExpectedDate\` for the specified cycle.

  #### Query

  ```graphql
  mutation subscriptionBillingCycleScheduleEdit($contractId: ID!, $index: Int!, $date: DateTime!) {
    subscriptionBillingCycleScheduleEdit(billingCycleInput: {contractId: $contractId, selector: {index: $index}}, input: {billingDate: $date, reason: BUYER_INITIATED}) {
      billingCycle {
        cycleIndex
        billingAttemptExpectedDate
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
    "contractId": "gid://shopify/SubscriptionContract/398475269",
    "index": 1,
    "date": "2021-12-31T07:00:00-05:00"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation subscriptionBillingCycleScheduleEdit($contractId: ID!, $index: Int!, $date: DateTime!) { subscriptionBillingCycleScheduleEdit(billingCycleInput: {contractId: $contractId, selector: {index: $index}}, input: {billingDate: $date, reason: BUYER_INITIATED}) { billingCycle { cycleIndex billingAttemptExpectedDate } userErrors { field message } } }",
   "variables": {
      "contractId": "gid://shopify/SubscriptionContract/398475269",
      "index": 1,
      "date": "2021-12-31T07:00:00-05:00"
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
    mutation subscriptionBillingCycleScheduleEdit($contractId: ID!, $index: Int!, $date: DateTime!) {
      subscriptionBillingCycleScheduleEdit(billingCycleInput: {contractId: $contractId, selector: {index: $index}}, input: {billingDate: $date, reason: BUYER_INITIATED}) {
        billingCycle {
          cycleIndex
          billingAttemptExpectedDate
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "contractId": "gid://shopify/SubscriptionContract/398475269",
          "index": 1,
          "date": "2021-12-31T07:00:00-05:00"
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
    mutation subscriptionBillingCycleScheduleEdit($contractId: ID!, $index: Int!, $date: DateTime!) {
      subscriptionBillingCycleScheduleEdit(billingCycleInput: {contractId: $contractId, selector: {index: $index}}, input: {billingDate: $date, reason: BUYER_INITIATED}) {
        billingCycle {
          cycleIndex
          billingAttemptExpectedDate
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "contractId": "gid://shopify/SubscriptionContract/398475269",
    "index": 1,
    "date": "2021-12-31T07:00:00-05:00"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation subscriptionBillingCycleScheduleEdit($contractId: ID!, $index: Int!, $date: DateTime!) {
        subscriptionBillingCycleScheduleEdit(billingCycleInput: {contractId: $contractId, selector: {index: $index}}, input: {billingDate: $date, reason: BUYER_INITIATED}) {
          billingCycle {
            cycleIndex
            billingAttemptExpectedDate
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "contractId": "gid://shopify/SubscriptionContract/398475269",
          "index": 1,
          "date": "2021-12-31T07:00:00-05:00"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation subscriptionBillingCycleScheduleEdit($contractId: ID!, $index: Int!, $date: DateTime!) {
    subscriptionBillingCycleScheduleEdit(billingCycleInput: {contractId: $contractId, selector: {index: $index}}, input: {billingDate: $date, reason: BUYER_INITIATED}) {
      billingCycle {
        cycleIndex
        billingAttemptExpectedDate
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "contractId": "gid://shopify/SubscriptionContract/398475269",
    "index": 1,
    "date": "2021-12-31T07:00:00-05:00"
  }'
  ```

  #### Response

  ```json
  {
    "subscriptionBillingCycleScheduleEdit": {
      "billingCycle": {
        "cycleIndex": 1,
        "billingAttemptExpectedDate": "2021-12-31T12:00:00Z"
      },
      "userErrors": []
    }
  }
  ```

* ### Skip a cycle

  #### Description

  Skips the billing and delivery for the billing cycle with cycle index \`1\`. The reason that is given for the skip is a customer request.

  #### Query

  ```graphql
  mutation subscriptionBillingCycleScheduleEdit($contractId: ID!, $index: Int!) {
    subscriptionBillingCycleScheduleEdit(billingCycleInput: {contractId: $contractId, selector: {index: $index}}, input: {skip: true, reason: BUYER_INITIATED}) {
      billingCycle {
        cycleIndex
        skipped
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
    "contractId": "gid://shopify/SubscriptionContract/398475269",
    "index": 1
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation subscriptionBillingCycleScheduleEdit($contractId: ID!, $index: Int!) { subscriptionBillingCycleScheduleEdit(billingCycleInput: {contractId: $contractId, selector: {index: $index}}, input: {skip: true, reason: BUYER_INITIATED}) { billingCycle { cycleIndex skipped } userErrors { field message } } }",
   "variables": {
      "contractId": "gid://shopify/SubscriptionContract/398475269",
      "index": 1
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
    mutation subscriptionBillingCycleScheduleEdit($contractId: ID!, $index: Int!) {
      subscriptionBillingCycleScheduleEdit(billingCycleInput: {contractId: $contractId, selector: {index: $index}}, input: {skip: true, reason: BUYER_INITIATED}) {
        billingCycle {
          cycleIndex
          skipped
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "contractId": "gid://shopify/SubscriptionContract/398475269",
          "index": 1
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
    mutation subscriptionBillingCycleScheduleEdit($contractId: ID!, $index: Int!) {
      subscriptionBillingCycleScheduleEdit(billingCycleInput: {contractId: $contractId, selector: {index: $index}}, input: {skip: true, reason: BUYER_INITIATED}) {
        billingCycle {
          cycleIndex
          skipped
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "contractId": "gid://shopify/SubscriptionContract/398475269",
    "index": 1
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation subscriptionBillingCycleScheduleEdit($contractId: ID!, $index: Int!) {
        subscriptionBillingCycleScheduleEdit(billingCycleInput: {contractId: $contractId, selector: {index: $index}}, input: {skip: true, reason: BUYER_INITIATED}) {
          billingCycle {
            cycleIndex
            skipped
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "contractId": "gid://shopify/SubscriptionContract/398475269",
          "index": 1
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation subscriptionBillingCycleScheduleEdit($contractId: ID!, $index: Int!) {
    subscriptionBillingCycleScheduleEdit(billingCycleInput: {contractId: $contractId, selector: {index: $index}}, input: {skip: true, reason: BUYER_INITIATED}) {
      billingCycle {
        cycleIndex
        skipped
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "contractId": "gid://shopify/SubscriptionContract/398475269",
    "index": 1
  }'
  ```

  #### Response

  ```json
  {
    "subscriptionBillingCycleScheduleEdit": {
      "billingCycle": {
        "cycleIndex": 1,
        "skipped": true
      },
      "userErrors": []
    }
  }
  ```

* ### subscriptionBillingCycleScheduleEdit reference
