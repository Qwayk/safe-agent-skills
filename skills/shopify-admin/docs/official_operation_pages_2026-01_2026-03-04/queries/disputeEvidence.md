---
title: disputeEvidence - GraphQL Admin
description: Returns a `ShopifyPaymentsDisputeEvidence` resource by ID.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/disputeEvidence'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/disputeEvidence.md'
---

# dispute​Evidence

query

Returns a `ShopifyPaymentsDisputeEvidence` resource by ID.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the `ShopifyPaymentsDisputeEvidence` to return.

***

## Possible returns

* Shopify​Payments​Dispute​Evidence

  [Shopify​Payments​Dispute​Evidence](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsDisputeEvidence)

  The evidence associated with the dispute.

  * access​Activity​Log

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The activity logs associated with the dispute evidence.

  * billing​Address

    [Mailing​Address](https://shopify.dev/docs/api/admin-graphql/latest/objects/MailingAddress)

    The billing address that's provided by the customer.

  * cancellation​Policy​Disclosure

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The cancellation policy disclosure associated with the dispute evidence.

  * cancellation​Policy​File

    [Shopify​Payments​Dispute​File​Upload](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsDisputeFileUpload)

    The cancellation policy file associated with the dispute evidence.

  * cancellation​Rebuttal

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The cancellation rebuttal associated with the dispute evidence.

  * customer​Communication​File

    [Shopify​Payments​Dispute​File​Upload](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsDisputeFileUpload)

    The customer communication file associated with the dispute evidence.

  * customer​Email​Address

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The customer's email address.

  * customer​First​Name

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The customer's first name.

  * customer​Last​Name

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The customer's last name.

  * customer​Purchase​Ip

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The customer purchase ip for this dispute evidence.

  * dispute

    [Shopify​Payments​Dispute!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsDispute)

    non-null

    The dispute associated with the evidence.

  * dispute​File​Uploads

    [\[Shopify​Payments​Dispute​File​Upload!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsDisputeFileUpload)

    non-null

    The file uploads associated with the dispute evidence.

  * fulfillments

    [\[Shopify​Payments​Dispute​Fulfillment!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsDisputeFulfillment)

    non-null

    The fulfillments associated with the dispute evidence.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * product​Description

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The product description for this dispute evidence.

  * refund​Policy​Disclosure

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The refund policy disclosure associated with the dispute evidence.

  * refund​Policy​File

    [Shopify​Payments​Dispute​File​Upload](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsDisputeFileUpload)

    The refund policy file associated with the dispute evidence.

  * refund​Refusal​Explanation

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The refund refusal explanation associated with dispute evidence.

  * service​Documentation​File

    [Shopify​Payments​Dispute​File​Upload](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsDisputeFileUpload)

    The service documentation file associated with the dispute evidence.

  * shipping​Address

    [Mailing​Address](https://shopify.dev/docs/api/admin-graphql/latest/objects/MailingAddress)

    The mailing address for shipping that's provided by the customer.

  * shipping​Documentation​File

    [Shopify​Payments​Dispute​File​Upload](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsDisputeFileUpload)

    The shipping documentation file associated with the dispute evidence.

  * submitted

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the dispute evidence is submitted.

  * uncategorized​File

    [Shopify​Payments​Dispute​File​Upload](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsDisputeFileUpload)

    The uncategorized file associated with the dispute evidence.

  * uncategorized​Text

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The uncategorized text for the dispute evidence.

***

## Examples

* ### Returns evidence associated with the dispute

  #### Query

  ```graphql
  query ShopifyPaymentsDisputeEvidenceShow($id: ID!) {
    disputeEvidence(id: $id) {
      dispute {
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
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/ShopifyPaymentsDisputeEvidence/819974671"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query ShopifyPaymentsDisputeEvidenceShow($id: ID!) { disputeEvidence(id: $id) { dispute { amount { amount currencyCode } evidenceDueBy evidenceSentOn finalizedOn id initiatedAt reasonDetails { reason networkReasonCode } status type } } }",
   "variables": {
      "id": "gid://shopify/ShopifyPaymentsDisputeEvidence/819974671"
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
    query ShopifyPaymentsDisputeEvidenceShow($id: ID!) {
      disputeEvidence(id: $id) {
        dispute {
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
    }`,
    {
      variables: {
          "id": "gid://shopify/ShopifyPaymentsDisputeEvidence/819974671"
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
    query ShopifyPaymentsDisputeEvidenceShow($id: ID!) {
      disputeEvidence(id: $id) {
        dispute {
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
    }
  QUERY

  variables = {
    "id": "gid://shopify/ShopifyPaymentsDisputeEvidence/819974671"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query ShopifyPaymentsDisputeEvidenceShow($id: ID!) {
        disputeEvidence(id: $id) {
          dispute {
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
      }`,
      "variables": {
          "id": "gid://shopify/ShopifyPaymentsDisputeEvidence/819974671"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query ShopifyPaymentsDisputeEvidenceShow($id: ID!) {
    disputeEvidence(id: $id) {
      dispute {
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
  }' \
  --variables \
  '{
    "id": "gid://shopify/ShopifyPaymentsDisputeEvidence/819974671"
  }'
  ```

  #### Response

  ```json
  {
    "disputeEvidence": {
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
  }
  ```
