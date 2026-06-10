---
title: subscriptionBillingCycleBulkResults - GraphQL Admin
description: >-
  Retrieves the results of the asynchronous job for the subscription billing
  cycle bulk action based on the specified job ID.

  This query can be used to obtain the billing cycles that match the criteria
  defined in the subscriptionBillingCycleBulkSearch and
  subscriptionBillingCycleBulkCharge mutations.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/subscriptionBillingCycleBulkResults
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/subscriptionBillingCycleBulkResults.md
---

# subscription​Billing​Cycle​Bulk​Results

query

Retrieves the results of the asynchronous job for the subscription billing cycle bulk action based on the specified job ID. This query can be used to obtain the billing cycles that match the criteria defined in the subscriptionBillingCycleBulkSearch and subscriptionBillingCycleBulkCharge mutations.

## SubscriptionBillingCycleConnection arguments

[SubscriptionBillingCycleConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/SubscriptionBillingCycleConnection)

* after

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* before

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* first

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* job​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the billing cycle bulk operation job.

* last

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

***

## Possible returns

* edges

  [\[Subscription​Billing​Cycle​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionBillingCycleEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Subscription​Billing​Cycle!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionBillingCycle)

  non-null

  A list of nodes that are contained in SubscriptionBillingCycleEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Get the list of the billing cycles targeted as part of the bulk action

  #### Description

  Retrieves a list containing the cycleIndex of the billing cycles targeted as part of the bulk action using the informed job id.

  #### Query

  ```graphql
  query SubscriptionBillingCycleBulkResults($jobId: ID!, $first: Int!, $after: String) {
    subscriptionBillingCycleBulkResults(first: $first, after: $after, jobId: $jobId) {
      pageInfo {
        startCursor
        endCursor
      }
      edges {
        node {
          cycleIndex
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "jobId": "gid://shopify/Job/0faf9493-b523-4c92-8e6e-59139254b03b",
    "first": 3
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query SubscriptionBillingCycleBulkResults($jobId: ID!, $first: Int!, $after: String) { subscriptionBillingCycleBulkResults(first: $first, after: $after, jobId: $jobId) { pageInfo { startCursor endCursor } edges { node { cycleIndex } } } }",
   "variables": {
      "jobId": "gid://shopify/Job/0faf9493-b523-4c92-8e6e-59139254b03b",
      "first": 3
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
    query SubscriptionBillingCycleBulkResults($jobId: ID!, $first: Int!, $after: String) {
      subscriptionBillingCycleBulkResults(first: $first, after: $after, jobId: $jobId) {
        pageInfo {
          startCursor
          endCursor
        }
        edges {
          node {
            cycleIndex
          }
        }
      }
    }`,
    {
      variables: {
          "jobId": "gid://shopify/Job/0faf9493-b523-4c92-8e6e-59139254b03b",
          "first": 3
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
    query SubscriptionBillingCycleBulkResults($jobId: ID!, $first: Int!, $after: String) {
      subscriptionBillingCycleBulkResults(first: $first, after: $after, jobId: $jobId) {
        pageInfo {
          startCursor
          endCursor
        }
        edges {
          node {
            cycleIndex
          }
        }
      }
    }
  QUERY

  variables = {
    "jobId": "gid://shopify/Job/0faf9493-b523-4c92-8e6e-59139254b03b",
    "first": 3
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query SubscriptionBillingCycleBulkResults($jobId: ID!, $first: Int!, $after: String) {
        subscriptionBillingCycleBulkResults(first: $first, after: $after, jobId: $jobId) {
          pageInfo {
            startCursor
            endCursor
          }
          edges {
            node {
              cycleIndex
            }
          }
        }
      }`,
      "variables": {
          "jobId": "gid://shopify/Job/0faf9493-b523-4c92-8e6e-59139254b03b",
          "first": 3
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query SubscriptionBillingCycleBulkResults($jobId: ID!, $first: Int!, $after: String) {
    subscriptionBillingCycleBulkResults(first: $first, after: $after, jobId: $jobId) {
      pageInfo {
        startCursor
        endCursor
      }
      edges {
        node {
          cycleIndex
        }
      }
    }
  }' \
  --variables \
  '{
    "jobId": "gid://shopify/Job/0faf9493-b523-4c92-8e6e-59139254b03b",
    "first": 3
  }'
  ```

  #### Response

  ```json
  {
    "subscriptionBillingCycleBulkResults": {
      "pageInfo": {
        "startCursor": "eyJsYXN0X2lkIjoyMzIzNzkyMjUsImxhc3RfdmFsdWUiOiIyMzIzNzkyMjUifQ==",
        "endCursor": "eyJsYXN0X2lkIjoyMzIzNzkyMjUsImxhc3RfdmFsdWUiOiIyMzIzNzkyMjUifQ=="
      },
      "edges": [
        {
          "node": {
            "cycleIndex": 1
          }
        }
      ]
    }
  }
  ```
