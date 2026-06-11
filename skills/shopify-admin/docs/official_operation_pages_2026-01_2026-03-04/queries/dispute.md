---
title: dispute - GraphQL Admin
description: Returns a `ShopifyPaymentsDispute` resource by ID.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/dispute'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/dispute.md'
---

# dispute

query

Returns a `ShopifyPaymentsDispute` resource by ID.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the `ShopifyPaymentsDispute` to return.

***

## Possible returns

* Shopify​Payments​Dispute

  [Shopify​Payments​Dispute](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsDispute)

  A dispute occurs when a buyer questions the legitimacy of a charge with their financial institution.

  * amount

    [Money​V2!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyV2)

    non-null

    The total amount disputed by the cardholder.

  * dispute​Evidence

    [Shopify​Payments​Dispute​Evidence!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsDisputeEvidence)

    non-null

    The evidence associated with the dispute.

  * evidence​Due​By

    [Date](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Date)

    The deadline for evidence submission.

  * evidence​Sent​On

    [Date](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Date)

    The date when evidence was sent. Returns null if evidence hasn't yet been sent.

  * finalized​On

    [Date](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Date)

    The date when this dispute was resolved. Returns null if the dispute isn't yet resolved.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * initiated​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date when this dispute was initiated.

  * legacy​Resource​Id

    [Unsigned​Int64!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/UnsignedInt64)

    non-null

    The ID of the corresponding resource in the REST Admin API.

  * order

    [Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order)

    The order that contains the charge that's under dispute.

  * reason​Details

    [Shopify​Payments​Dispute​Reason​Details!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsDisputeReasonDetails)

    non-null

    The reason of the dispute.

  * status

    [Dispute​Status!](https://shopify.dev/docs/api/admin-graphql/latest/enums/DisputeStatus)

    non-null

    The current state of the dispute.

  * type

    [Dispute​Type!](https://shopify.dev/docs/api/admin-graphql/latest/enums/DisputeType)

    non-null

    Indicates if this dispute is still in the inquiry phase or has turned into a chargeback.

***

## Examples

* ### Return a single dispute

  #### Query

  ```graphql
  query ShopifyPaymentsDisputesShow($id: ID!) {
    dispute(id: $id) {
      amount {
        amount
        currencyCode
      }
      evidenceDueBy
      evidenceSentOn
      finalizedOn
      id
      initiatedAt
      reasonDetails {
        reason
        networkReasonCode
      }
      status
      type
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/ShopifyPaymentsDispute/598735659"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query ShopifyPaymentsDisputesShow($id: ID!) { dispute(id: $id) { amount { amount currencyCode } evidenceDueBy evidenceSentOn finalizedOn id initiatedAt reasonDetails { reason networkReasonCode } status type } }",
   "variables": {
      "id": "gid://shopify/ShopifyPaymentsDispute/598735659"
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
    query ShopifyPaymentsDisputesShow($id: ID!) {
      dispute(id: $id) {
        amount {
          amount
          currencyCode
        }
        evidenceDueBy
        evidenceSentOn
        finalizedOn
        id
        initiatedAt
        reasonDetails {
          reason
          networkReasonCode
        }
        status
        type
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/ShopifyPaymentsDispute/598735659"
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
    query ShopifyPaymentsDisputesShow($id: ID!) {
      dispute(id: $id) {
        amount {
          amount
          currencyCode
        }
        evidenceDueBy
        evidenceSentOn
        finalizedOn
        id
        initiatedAt
        reasonDetails {
          reason
          networkReasonCode
        }
        status
        type
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/ShopifyPaymentsDispute/598735659"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query ShopifyPaymentsDisputesShow($id: ID!) {
        dispute(id: $id) {
          amount {
            amount
            currencyCode
          }
          evidenceDueBy
          evidenceSentOn
          finalizedOn
          id
          initiatedAt
          reasonDetails {
            reason
            networkReasonCode
          }
          status
          type
        }
      }`,
      "variables": {
          "id": "gid://shopify/ShopifyPaymentsDispute/598735659"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query ShopifyPaymentsDisputesShow($id: ID!) {
    dispute(id: $id) {
      amount {
        amount
        currencyCode
      }
      evidenceDueBy
      evidenceSentOn
      finalizedOn
      id
      initiatedAt
      reasonDetails {
        reason
        networkReasonCode
      }
      status
      type
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/ShopifyPaymentsDispute/598735659"
  }'
  ```

  #### Response

  ```json
  {
    "dispute": {
      "amount": {
        "amount": "11.5",
        "currencyCode": "USD"
      },
      "evidenceDueBy": "2024-11-20T19:00:00-05:00",
      "evidenceSentOn": null,
      "finalizedOn": null,
      "id": "gid://shopify/ShopifyPaymentsDispute/598735659",
      "initiatedAt": "2013-05-04T00:00:00Z",
      "reasonDetails": {
        "reason": "FRAUDULENT",
        "networkReasonCode": "4827"
      },
      "status": "NEEDS_RESPONSE",
      "type": "CHARGEBACK"
    }
  }
  ```
