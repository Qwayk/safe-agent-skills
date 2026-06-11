---
title: productResourceFeedback - GraphQL Admin
description: >-
  Retrieves product resource feedback for the currently authenticated app,
  providing insights into product data quality, completeness, and optimization
  opportunities. This feedback helps apps guide merchants toward better product
  listings and improved store performance.


  For example, an SEO app might receive feedback indicating that certain
  products lack meta descriptions or have suboptimal titles, enabling the app to
  provide specific recommendations for improving search visibility and
  conversion rates.


  Use `ProductResourceFeedback` to:

  - Display product optimization recommendations to merchants

  - Identify data quality issues across product catalogs

  - Build product improvement workflows and guided experiences

  - Track progress on product listing completeness and quality

  - Implement automated product auditing and scoring systems

  - Generate reports on catalog health and optimization opportunities

  - Provide contextual suggestions within product editing interfaces


  The feedback system evaluates products against various criteria including SEO
  best practices, required fields, media quality, and sales channel
  requirements. Each feedback item includes specific details about the issue,
  suggested improvements, and priority levels.


  Feedback is app-specific and reflects the particular focus of your application
  - marketing apps receive different insights than inventory management apps.
  The system continuously updates as merchants make changes, providing real-time
  guidance for product optimization.


  This resource is particularly valuable for apps that help merchants improve
  their product listings, optimize for search engines, or enhance their overall
  catalog quality. The feedback enables proactive suggestions rather than
  reactive problem-solving.


  Learn more about [product
  optimization](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/productResourceFeedback
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/productResourceFeedback.md
---

# product​Resource​Feedback

query

Requires `read_resource_feedbacks` access scope. Also: App must be configured to use the Storefront API or as a Sales Channel.

Retrieves product resource feedback for the currently authenticated app, providing insights into product data quality, completeness, and optimization opportunities. This feedback helps apps guide merchants toward better product listings and improved store performance.

For example, an SEO app might receive feedback indicating that certain products lack meta descriptions or have suboptimal titles, enabling the app to provide specific recommendations for improving search visibility and conversion rates.

Use `ProductResourceFeedback` to:

* Display product optimization recommendations to merchants
* Identify data quality issues across product catalogs
* Build product improvement workflows and guided experiences
* Track progress on product listing completeness and quality
* Implement automated product auditing and scoring systems
* Generate reports on catalog health and optimization opportunities
* Provide contextual suggestions within product editing interfaces

The feedback system evaluates products against various criteria including SEO best practices, required fields, media quality, and sales channel requirements. Each feedback item includes specific details about the issue, suggested improvements, and priority levels.

Feedback is app-specific and reflects the particular focus of your application - marketing apps receive different insights than inventory management apps. The system continuously updates as merchants make changes, providing real-time guidance for product optimization.

This resource is particularly valuable for apps that help merchants improve their product listings, optimize for search engines, or enhance their overall catalog quality. The feedback enables proactive suggestions rather than reactive problem-solving.

Learn more about [product optimization](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product).

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The product associated with the resource feedback.

***

## Possible returns

* Product​Resource​Feedback

  [Product​Resource​Feedback](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductResourceFeedback)

  Reports the status of product for a Sales Channel or Storefront API. This might include why a product is not available in a Sales Channel and how a merchant might fix this.

  * feedback​Generated​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The time when the feedback was generated. Used to help determine whether incoming feedback is outdated compared to existing feedback.

  * messages

    [\[String!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The feedback messages presented to the merchant.

  * product​Id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    The ID of the product associated with the feedback.

  * product​Updated​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The timestamp of the product associated with the feedback.

  * state

    [Resource​Feedback​State!](https://shopify.dev/docs/api/admin-graphql/latest/enums/ResourceFeedbackState)

    non-null

    Conveys the state of the feedback and whether it requires merchant action or not.

***

## Examples

* ### Get a product resource feedback record by ID that doesn't exist

  #### Description

  Trying to retrieve a feedback for a non-existent product returns \`null\`.

  #### Query

  ```graphql
  query {
    productResourceFeedback(id: "gid://shopify/Product/-1") {
      feedbackGeneratedAt
      messages
      productId
      productUpdatedAt
      state
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
  "query": "query { productResourceFeedback(id: \"gid://shopify/Product/-1\") { feedbackGeneratedAt messages productId productUpdatedAt state } }"
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
      productResourceFeedback(id: "gid://shopify/Product/-1") {
        feedbackGeneratedAt
        messages
        productId
        productUpdatedAt
        state
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
      productResourceFeedback(id: "gid://shopify/Product/-1") {
        feedbackGeneratedAt
        messages
        productId
        productUpdatedAt
        state
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
      productResourceFeedback(id: "gid://shopify/Product/-1") {
        feedbackGeneratedAt
        messages
        productId
        productUpdatedAt
        state
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    productResourceFeedback(id: "gid://shopify/Product/-1") {
      feedbackGeneratedAt
      messages
      productId
      productUpdatedAt
      state
    }
  }'
  ```

  #### Response

  ```json
  {
    "productResourceFeedback": null
  }
  ```

* ### Receive a list of all Product ResourceFeedbacks

  #### Query

  ```graphql
  query {
    productResourceFeedback(id: "gid://shopify/Product/1048875085") {
      feedbackGeneratedAt
      messages
      productId
      productUpdatedAt
      state
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
  "query": "query { productResourceFeedback(id: \"gid://shopify/Product/1048875085\") { feedbackGeneratedAt messages productId productUpdatedAt state } }"
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
      productResourceFeedback(id: "gid://shopify/Product/1048875085") {
        feedbackGeneratedAt
        messages
        productId
        productUpdatedAt
        state
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
      productResourceFeedback(id: "gid://shopify/Product/1048875085") {
        feedbackGeneratedAt
        messages
        productId
        productUpdatedAt
        state
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
      productResourceFeedback(id: "gid://shopify/Product/1048875085") {
        feedbackGeneratedAt
        messages
        productId
        productUpdatedAt
        state
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    productResourceFeedback(id: "gid://shopify/Product/1048875085") {
      feedbackGeneratedAt
      messages
      productId
      productUpdatedAt
      state
    }
  }'
  ```

  #### Response

  ```json
  {
    "productResourceFeedback": {
      "feedbackGeneratedAt": "2024-11-14T20:48:48Z",
      "messages": [
        "Needs an image."
      ],
      "productId": "gid://shopify/Product/1048875085",
      "productUpdatedAt": "2024-11-14T20:48:48Z",
      "state": "REQUIRES_ACTION"
    }
  }
  ```
