---
title: appPurchaseOneTimeCreate - GraphQL Admin
description: >-
  Creates a one-time charge for app features or services that don't require
  recurring billing. This mutation is ideal for apps that sell individual
  features, premium content, or services on a per-use basis rather than
  subscription models.


  For example, a design app might charge merchants once for premium templates,
  or a marketing app could bill for individual campaign setups without ongoing
  monthly fees.


  Use the `AppPurchaseOneTimeCreate` mutation to:

  - Charge for premium features or content purchases

  - Bill for professional services or setup fees

  - Generate revenue from one-time digital product sales


  The mutation returns a confirmation URL that merchants must visit to approve
  the charge. Test and development stores are not charged, allowing safe testing
  of billing flows.


  Explore one-time billing options on the [app purchases
  page](https://shopify.dev/docs/apps/launch/billing/support-one-time-purchases).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/appPurchaseOneTimeCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/appPurchaseOneTimeCreate.md
---

# app​Purchase​One​Time​Create

mutation

Creates a one-time charge for app features or services that don't require recurring billing. This mutation is ideal for apps that sell individual features, premium content, or services on a per-use basis rather than subscription models.

For example, a design app might charge merchants once for premium templates, or a marketing app could bill for individual campaign setups without ongoing monthly fees.

Use the `AppPurchaseOneTimeCreate` mutation to:

* Charge for premium features or content purchases
* Bill for professional services or setup fees
* Generate revenue from one-time digital product sales

The mutation returns a confirmation URL that merchants must visit to approve the charge. Test and development stores are not charged, allowing safe testing of billing flows.

Explore one-time billing options on the [app purchases page](https://shopify.dev/docs/apps/launch/billing/support-one-time-purchases).

## Arguments

* name

  [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  The name of the one-time purchase from the app.

* price

  [Money​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MoneyInput)

  required

  The amount to be charged to the store for the app one-time purchase.

* return​Url

  [URL!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

  required

  The URL where the merchant is redirected after approving the app one-time purchase.

* test

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Whether the app one-time purchase is a test transaction.

***

## App​Purchase​One​Time​Create​Payload returns

* app​Purchase​One​Time

  [App​Purchase​One​Time](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppPurchaseOneTime)

  The newly created app one-time purchase.

* confirmation​Url

  [URL](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

  The URL that the merchant can access to approve or decline the newly created app one-time purchase.

  If the merchant declines, then the merchant is redirected to the app and receives a notification message stating that the charge was declined. If the merchant approves and they're successfully invoiced, then the state of the charge changes from `pending` to `active`.

  You get paid after the charge is activated.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Creates an application charge

  #### Description

  Summarizes the service rendered in the \`name\` field.

  #### Query

  ```graphql
  mutation AppPurchaseOneTimeCreate($name: String!, $price: MoneyInput!, $returnUrl: URL!) {
    appPurchaseOneTimeCreate(name: $name, returnUrl: $returnUrl, price: $price) {
      userErrors {
        field
        message
      }
      appPurchaseOneTime {
        createdAt
        id
      }
      confirmationUrl
    }
  }
  ```

  #### Variables

  ```json
  {
    "name": "1000 imported orders.",
    "returnUrl": "http://super-duper.shopifyapps.com/",
    "price": {
      "amount": 10,
      "currencyCode": "USD"
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
  "query": "mutation AppPurchaseOneTimeCreate($name: String!, $price: MoneyInput!, $returnUrl: URL!) { appPurchaseOneTimeCreate(name: $name, returnUrl: $returnUrl, price: $price) { userErrors { field message } appPurchaseOneTime { createdAt id } confirmationUrl } }",
   "variables": {
      "name": "1000 imported orders.",
      "returnUrl": "http://super-duper.shopifyapps.com/",
      "price": {
        "amount": 10,
        "currencyCode": "USD"
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
    mutation AppPurchaseOneTimeCreate($name: String!, $price: MoneyInput!, $returnUrl: URL!) {
      appPurchaseOneTimeCreate(name: $name, returnUrl: $returnUrl, price: $price) {
        userErrors {
          field
          message
        }
        appPurchaseOneTime {
          createdAt
          id
        }
        confirmationUrl
      }
    }`,
    {
      variables: {
          "name": "1000 imported orders.",
          "returnUrl": "http://super-duper.shopifyapps.com/",
          "price": {
              "amount": 10,
              "currencyCode": "USD"
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
    mutation AppPurchaseOneTimeCreate($name: String!, $price: MoneyInput!, $returnUrl: URL!) {
      appPurchaseOneTimeCreate(name: $name, returnUrl: $returnUrl, price: $price) {
        userErrors {
          field
          message
        }
        appPurchaseOneTime {
          createdAt
          id
        }
        confirmationUrl
      }
    }
  QUERY

  variables = {
    "name": "1000 imported orders.",
    "returnUrl": "http://super-duper.shopifyapps.com/",
    "price": {
      "amount": 10,
      "currencyCode": "USD"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation AppPurchaseOneTimeCreate($name: String!, $price: MoneyInput!, $returnUrl: URL!) {
        appPurchaseOneTimeCreate(name: $name, returnUrl: $returnUrl, price: $price) {
          userErrors {
            field
            message
          }
          appPurchaseOneTime {
            createdAt
            id
          }
          confirmationUrl
        }
      }`,
      "variables": {
          "name": "1000 imported orders.",
          "returnUrl": "http://super-duper.shopifyapps.com/",
          "price": {
              "amount": 10,
              "currencyCode": "USD"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation AppPurchaseOneTimeCreate($name: String!, $price: MoneyInput!, $returnUrl: URL!) {
    appPurchaseOneTimeCreate(name: $name, returnUrl: $returnUrl, price: $price) {
      userErrors {
        field
        message
      }
      appPurchaseOneTime {
        createdAt
        id
      }
      confirmationUrl
    }
  }' \
  --variables \
  '{
    "name": "1000 imported orders.",
    "returnUrl": "http://super-duper.shopifyapps.com/",
    "price": {
      "amount": 10,
      "currencyCode": "USD"
    }
  }'
  ```

  #### Response

  ```json
  {
    "appPurchaseOneTimeCreate": {
      "userErrors": [],
      "appPurchaseOneTime": {
        "createdAt": "2024-11-21T22:47:04Z",
        "id": "gid://shopify/AppPurchaseOneTime/1017262352"
      },
      "confirmationUrl": "https://billingshop.myshopify.com/admin/charges/193172482/1017262352/ApplicationCharge/confirm_application_charge?signature=BAh7BzoHaWRpBBAxojw6EmF1dG9fYWN0aXZhdGVU--a03eedf9ef12d714906af085ebc2aa3d97aa9466"
    }
  }
  ```

* ### appPurchaseOneTimeCreate reference
