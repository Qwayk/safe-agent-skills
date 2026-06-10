---
title: abandonmentByAbandonedCheckoutId - GraphQL Admin
description: Returns an Abandonment by the Abandoned Checkout ID.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/abandonmentByAbandonedCheckoutId
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/abandonmentByAbandonedCheckoutId.md
---

# abandonment​By​Abandoned​Checkout​Id

query

Returns an Abandonment by the Abandoned Checkout ID.

## Arguments

* abandoned​Checkout​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the Abandoned Checkout ID to query by.

***

## Possible returns

* Abandonment

  [Abandonment](https://shopify.dev/docs/api/admin-graphql/latest/objects/Abandonment)

  Tracks a [customer](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)'s incomplete shopping journey, whether they abandoned while browsing [products](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product), adding items to cart, or during checkout. Provides data about the customer's behavior and products they interacted with.

  The abandonment includes fields that indicate whether the customer has completed any [orders](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order) or [draft orders](https://shopify.dev/docs/api/admin-graphql/latest/objects/DraftOrder) after the abandonment occurred. It also tracks when emails were sent and how long since the customer's last activity across different abandonment types.

  * abandoned​Checkout​Payload

    [Abandoned​Checkout](https://shopify.dev/docs/api/admin-graphql/latest/objects/AbandonedCheckout)

    The abandonment payload for the abandoned checkout.

  * abandonment​Type

    [Abandonment​Abandonment​Type!](https://shopify.dev/docs/api/admin-graphql/latest/enums/AbandonmentAbandonmentType)

    non-null

    The abandonment type.

  * app

    [App!](https://shopify.dev/docs/api/admin-graphql/latest/objects/App)

    non-null

    The app associated with an abandoned checkout.

  * cart​Url

    [URL](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    Permalink to the cart page.

  * created​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the abandonment was created.

  * customer

    [Customer!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)

    non-null

    The customer who abandoned this event.

  * customer​Has​No​Draft​Order​Since​Abandonment

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the customer has a draft order since this abandonment has been abandoned.

  * customer​Has​No​Order​Since​Abandonment

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the customer has completed an order since this checkout has been abandoned.

  * days​Since​Last​Abandonment​Email

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    The number of days since the last abandonment email was sent to the customer.

  * email​Sent​At

    [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    When the email was sent, if that's the case.

  * email​State

    [Abandonment​Email​State](https://shopify.dev/docs/api/admin-graphql/latest/enums/AbandonmentEmailState)

    The email state (e.g., sent or not sent).

  * hours​Since​Last​Abandoned​Checkout

    [Float](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Float)

    The number of hours since the customer has last abandoned a checkout.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * inventory​Available

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the products in abandonment are available.

  * is​From​Custom​Storefront

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the abandonment event comes from a custom storefront channel.

  * is​From​Online​Store

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the abandonment event comes from the Online Store sales channel.

  * is​From​Shop​App

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the abandonment event comes from the Shop app sales channel.

  * is​From​Shop​Pay

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the abandonment event comes from Shop Pay.

  * is​Most​Significant​Abandonment

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the customer didn't complete another most significant step since this abandonment.

  * last​Browse​Abandonment​Date

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date for the latest browse abandonment.

  * last​Cart​Abandonment​Date

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date for the latest cart abandonment.

  * last​Checkout​Abandonment​Date

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date for the latest checkout abandonment.

  * most​Recent​Step

    [Abandonment​Abandonment​Type!](https://shopify.dev/docs/api/admin-graphql/latest/enums/AbandonmentAbandonmentType)

    non-null

    The most recent step type.

  * products​Added​To​Cart

    [Customer​Visit​Product​Info​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/CustomerVisitProductInfoConnection)

    non-null

    The products added to the cart during the customer abandoned visit.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * last

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * before

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * reverse

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Reverse the order of the underlying list.

    ***

  * products​Viewed

    [Customer​Visit​Product​Info​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/CustomerVisitProductInfoConnection)

    non-null

    The products viewed during the customer abandoned visit.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * last

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * before

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * reverse

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Reverse the order of the underlying list.

    ***

  * visit​Started​At

    [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    The date and time when the visit started.

***

## Examples

* ### abandonmentByAbandonedCheckoutId reference
