---
title: paymentTermsTemplates - GraphQL Admin
description: The list of payment terms templates eligible for all shops and users.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/paymentTermsTemplates
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/paymentTermsTemplates.md
---

# payment​Terms​Templates

query

The list of payment terms templates eligible for all shops and users.

## Arguments

* payment​Terms​Type

  [Payment​Terms​Type](https://shopify.dev/docs/api/admin-graphql/latest/enums/PaymentTermsType)

  The payment terms type to filter the payment terms templates list.

***

## Possible returns

* Payment​Terms​Template

  [\[Payment​Terms​Template!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PaymentTermsTemplate)

  Represents the payment terms template object.

  * description

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The description of the payment terms template.

  * due​In​Days

    [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    The number of days between the issued date and due date if this is the net type of payment terms.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The name of the payment terms template.

  * payment​Terms​Type

    [Payment​Terms​Type!](https://shopify.dev/docs/api/admin-graphql/latest/enums/PaymentTermsType)

    non-null

    The type of the payment terms template.

  * translated​Name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The translated payment terms template name.

***

## Examples

* ### Get the available payment terms templates

  #### Description

  The following query retrieves the available payment terms templates.

  #### Query

  ```graphql
  query {
    paymentTermsTemplates {
      id
      name
      paymentTermsType
      dueInDays
      description
      translatedName
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
  "query": "query { paymentTermsTemplates { id name paymentTermsType dueInDays description translatedName } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query {
      paymentTermsTemplates {
        id
        name
        paymentTermsType
        dueInDays
        description
        translatedName
      }
    }`,
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
    query {
      paymentTermsTemplates {
        id
        name
        paymentTermsType
        dueInDays
        description
        translatedName
      }
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `query {
      paymentTermsTemplates {
        id
        name
        paymentTermsType
        dueInDays
        description
        translatedName
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    paymentTermsTemplates {
      id
      name
      paymentTermsType
      dueInDays
      description
      translatedName
    }
  }'
  ```

  #### Response

  ```json
  {
    "paymentTermsTemplates": [
      {
        "id": "gid://shopify/PaymentTermsTemplate/1",
        "name": "Due on receipt",
        "paymentTermsType": "RECEIPT",
        "dueInDays": null,
        "description": "Due on receipt",
        "translatedName": "Due on receipt"
      },
      {
        "id": "gid://shopify/PaymentTermsTemplate/9",
        "name": "Due on fulfillment",
        "paymentTermsType": "FULFILLMENT",
        "dueInDays": null,
        "description": "Due on fulfillment",
        "translatedName": "Due on fulfillment"
      },
      {
        "id": "gid://shopify/PaymentTermsTemplate/2",
        "name": "Net 7",
        "paymentTermsType": "NET",
        "dueInDays": 7,
        "description": "Within 7 days",
        "translatedName": "Net 7"
      },
      {
        "id": "gid://shopify/PaymentTermsTemplate/3",
        "name": "Net 15",
        "paymentTermsType": "NET",
        "dueInDays": 15,
        "description": "Within 15 days",
        "translatedName": "Net 15"
      },
      {
        "id": "gid://shopify/PaymentTermsTemplate/4",
        "name": "Net 30",
        "paymentTermsType": "NET",
        "dueInDays": 30,
        "description": "Within 30 days",
        "translatedName": "Net 30"
      },
      {
        "id": "gid://shopify/PaymentTermsTemplate/8",
        "name": "Net 45",
        "paymentTermsType": "NET",
        "dueInDays": 45,
        "description": "Within 45 days",
        "translatedName": "Net 45"
      },
      {
        "id": "gid://shopify/PaymentTermsTemplate/5",
        "name": "Net 60",
        "paymentTermsType": "NET",
        "dueInDays": 60,
        "description": "Within 60 days",
        "translatedName": "Net 60"
      },
      {
        "id": "gid://shopify/PaymentTermsTemplate/6",
        "name": "Net 90",
        "paymentTermsType": "NET",
        "dueInDays": 90,
        "description": "Within 90 days",
        "translatedName": "Net 90"
      },
      {
        "id": "gid://shopify/PaymentTermsTemplate/7",
        "name": "Fixed",
        "paymentTermsType": "FIXED",
        "dueInDays": null,
        "description": "Fixed date",
        "translatedName": "Fixed"
      }
    ]
  }
  ```
