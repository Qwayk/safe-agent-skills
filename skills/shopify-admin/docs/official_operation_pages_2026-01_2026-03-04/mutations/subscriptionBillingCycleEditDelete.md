---
title: subscriptionBillingCycleEditDelete - GraphQL Admin
description: >-
  Delete the schedule and contract edits of the selected subscription billing
  cycle.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/subscriptionBillingCycleEditDelete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/subscriptionBillingCycleEditDelete.md
---

# subscription​Billing​Cycle​Edit​Delete

mutation

Requires `write_own_subscription_contracts` access scope. Also: The user must have manage\_orders\_information permission.

Delete the schedule and contract edits of the selected subscription billing cycle.

## Arguments

* billing​Cycle​Input

  [Subscription​Billing​Cycle​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/SubscriptionBillingCycleInput)

  required

  Input object used to select and use billing cycles.

***

## Subscription​Billing​Cycle​Edit​Delete​Payload returns

* billing​Cycles

  [\[Subscription​Billing​Cycle!\]](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionBillingCycle)

  The list of updated billing cycles.

* user​Errors

  [\[Subscription​Billing​Cycle​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionBillingCycleUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Deletes the edits on a future billing cycle

  #### Description

  Deletes the schedule and contract edits on the billing cycle with cycle index \`1\`, and reverts the schedule and contract to the information on the base subscription contract.

  #### Query

  ```graphql
  mutation subscriptionBillingCycleEditDelete($contractId: ID!, $index: Int!) {
    subscriptionBillingCycleEditDelete(billingCycleInput: {contractId: $contractId, selector: {index: $index}}) {
      billingCycles {
        cycleStartAt
        cycleEndAt
        cycleIndex
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
  "query": "mutation subscriptionBillingCycleEditDelete($contractId: ID!, $index: Int!) { subscriptionBillingCycleEditDelete(billingCycleInput: {contractId: $contractId, selector: {index: $index}}) { billingCycles { cycleStartAt cycleEndAt cycleIndex } userErrors { field message } } }",
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
    mutation subscriptionBillingCycleEditDelete($contractId: ID!, $index: Int!) {
      subscriptionBillingCycleEditDelete(billingCycleInput: {contractId: $contractId, selector: {index: $index}}) {
        billingCycles {
          cycleStartAt
          cycleEndAt
          cycleIndex
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
    mutation subscriptionBillingCycleEditDelete($contractId: ID!, $index: Int!) {
      subscriptionBillingCycleEditDelete(billingCycleInput: {contractId: $contractId, selector: {index: $index}}) {
        billingCycles {
          cycleStartAt
          cycleEndAt
          cycleIndex
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
      "query": `mutation subscriptionBillingCycleEditDelete($contractId: ID!, $index: Int!) {
        subscriptionBillingCycleEditDelete(billingCycleInput: {contractId: $contractId, selector: {index: $index}}) {
          billingCycles {
            cycleStartAt
            cycleEndAt
            cycleIndex
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
  'mutation subscriptionBillingCycleEditDelete($contractId: ID!, $index: Int!) {
    subscriptionBillingCycleEditDelete(billingCycleInput: {contractId: $contractId, selector: {index: $index}}) {
      billingCycles {
        cycleStartAt
        cycleEndAt
        cycleIndex
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
    "subscriptionBillingCycleEditDelete": {
      "billingCycles": [
        {
          "cycleStartAt": "2021-12-15T15:33:01Z",
          "cycleEndAt": "2022-01-01T12:00:00Z",
          "cycleIndex": 1
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### subscriptionBillingCycleEditDelete reference
