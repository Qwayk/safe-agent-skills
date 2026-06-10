---
title: subscriptionBillingCycleBulkCharge - GraphQL Admin
description: >-
  Asynchronously queries and charges all subscription billing cycles whose
  [billingAttemptExpectedDate](https://shopify.dev/api/admin-graphql/latest/objects/SubscriptionBillingCycle#field-billingattemptexpecteddate)
  values fall within a specified date range and meet additional filtering
  criteria. The results of this action can be retrieved using the
  [subscriptionBillingCycleBulkResults](https://shopify.dev/api/admin-graphql/latest/queries/subscriptionBillingCycleBulkResults)
  query.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/subscriptionBillingCycleBulkCharge
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/subscriptionBillingCycleBulkCharge.md
---

# subscription​Billing​Cycle​Bulk​Charge

mutation

Requires `write_own_subscription_contracts` access scope. Also: The user must have manage\_orders\_information permission.

Asynchronously queries and charges all subscription billing cycles whose [billingAttemptExpectedDate](https://shopify.dev/api/admin-graphql/latest/objects/SubscriptionBillingCycle#field-billingattemptexpecteddate) values fall within a specified date range and meet additional filtering criteria. The results of this action can be retrieved using the [subscriptionBillingCycleBulkResults](https://shopify.dev/api/admin-graphql/latest/queries/subscriptionBillingCycleBulkResults) query.

## Arguments

* billing​Attempt​Expected​Date​Range

  [Subscription​Billing​Cycles​Date​Range​Selector!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/SubscriptionBillingCyclesDateRangeSelector)

  required

  Specifies the date range within which the `billingAttemptExpectedDate` values of the billing cycles should fall.

* filters

  [Subscription​Billing​Cycle​Bulk​Filters](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/SubscriptionBillingCycleBulkFilters)

  Criteria to filter the billing cycles on which the action is executed.

* inventory​Policy

  [Subscription​Billing​Attempt​Inventory​Policy](https://shopify.dev/docs/api/admin-graphql/latest/enums/SubscriptionBillingAttemptInventoryPolicy)

  Default:PRODUCT\_VARIANT\_INVENTORY\_POLICY

  The behaviour to use when updating inventory.

***

## Subscription​Billing​Cycle​Bulk​Charge​Payload returns

* job

  [Job](https://shopify.dev/docs/api/admin-graphql/latest/objects/Job)

  The asynchronous job that performs the action on the targeted billing cycles.

* user​Errors

  [\[Subscription​Billing​Cycle​Bulk​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionBillingCycleBulkUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a job to charge all subscription billing cycles in time range

  #### Description

  Creates a job to charge all subscription billing cycles between 2023-02-01 and 2023-02-02.

  #### Query

  ```graphql
  mutation($startDate: DateTime!, $endDate: DateTime!) {
    subscriptionBillingCycleBulkCharge(billingAttemptExpectedDateRange: {startDate: $startDate, endDate: $endDate}) {
      job {
        id
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "startDate": "2023-02-01T00:00:00-05:00",
    "endDate": "2023-02-02T23:59:59-05:00"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation($startDate: DateTime!, $endDate: DateTime!) { subscriptionBillingCycleBulkCharge(billingAttemptExpectedDateRange: {startDate: $startDate, endDate: $endDate}) { job { id } } }",
   "variables": {
      "startDate": "2023-02-01T00:00:00-05:00",
      "endDate": "2023-02-02T23:59:59-05:00"
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
    mutation($startDate: DateTime!, $endDate: DateTime!) {
      subscriptionBillingCycleBulkCharge(billingAttemptExpectedDateRange: {startDate: $startDate, endDate: $endDate}) {
        job {
          id
        }
      }
    }`,
    {
      variables: {
          "startDate": "2023-02-01T00:00:00-05:00",
          "endDate": "2023-02-02T23:59:59-05:00"
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
    mutation($startDate: DateTime!, $endDate: DateTime!) {
      subscriptionBillingCycleBulkCharge(billingAttemptExpectedDateRange: {startDate: $startDate, endDate: $endDate}) {
        job {
          id
        }
      }
    }
  QUERY

  variables = {
    "startDate": "2023-02-01T00:00:00-05:00",
    "endDate": "2023-02-02T23:59:59-05:00"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation($startDate: DateTime!, $endDate: DateTime!) {
        subscriptionBillingCycleBulkCharge(billingAttemptExpectedDateRange: {startDate: $startDate, endDate: $endDate}) {
          job {
            id
          }
        }
      }`,
      "variables": {
          "startDate": "2023-02-01T00:00:00-05:00",
          "endDate": "2023-02-02T23:59:59-05:00"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation($startDate: DateTime!, $endDate: DateTime!) {
    subscriptionBillingCycleBulkCharge(billingAttemptExpectedDateRange: {startDate: $startDate, endDate: $endDate}) {
      job {
        id
      }
    }
  }' \
  --variables \
  '{
    "startDate": "2023-02-01T00:00:00-05:00",
    "endDate": "2023-02-02T23:59:59-05:00"
  }'
  ```

  #### Response

  ```json
  {
    "subscriptionBillingCycleBulkCharge": {
      "job": {
        "id": "gid://shopify/Job/99ff28fc-980d-48ef-a190-1a1973fb5ed3"
      }
    }
  }
  ```

* ### subscriptionBillingCycleBulkCharge reference
