---
title: businessEntities - GraphQL Admin
description: >-
  Returns the list of [business
  entities](https://shopify.dev/docs/api/admin-graphql/latest/objects/BusinessEntity)
  associated with the shop. Use this query to retrieve business entities for
  assigning to markets, managing payment providers per entity, or viewing entity
  attribution on orders.


  Each shop can have multiple business entities with one designated as primary.
  To identify the primary entity in the query results, set the
  [`primary`](https://shopify.dev/docs/api/admin-graphql/latest/queries/businessEntities#returns-BusinessEntity.fields.primary)
  field to `true`.


  Learn more about [managing multiple legal
  entities](https://shopify.dev/docs/apps/build/markets/multiple-entities).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/businessEntities'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/businessEntities.md
---

# business​Entities

query

Returns the list of [business entities](https://shopify.dev/docs/api/admin-graphql/latest/objects/BusinessEntity) associated with the shop. Use this query to retrieve business entities for assigning to markets, managing payment providers per entity, or viewing entity attribution on orders.

Each shop can have multiple business entities with one designated as primary. To identify the primary entity in the query results, set the [`primary`](https://shopify.dev/docs/api/admin-graphql/latest/queries/businessEntities#returns-BusinessEntity.fields.primary) field to `true`.

Learn more about [managing multiple legal entities](https://shopify.dev/docs/apps/build/markets/multiple-entities).

## Possible returns

* Business​Entity

  [\[Business​Entity!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/BusinessEntity)

  A legal entity through which a merchant operates. Each business entity contains its own [`BusinessEntityAddress`](https://shopify.dev/docs/api/admin-graphql/latest/objects/BusinessEntityAddress), company information, and can be associated with its own [`ShopifyPaymentsAccount`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsAccount). [`Market`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Market) objects can be assigned to a business entity to determine payment processing and [`Order`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order) attribution.

  Every shop must have one primary business entity. Additional entities enable international operations by establishing legal presence in multiple countries.

  Learn more about [managing multiple legal entities](https://shopify.dev/docs/apps/build/markets/multiple-entities).

  * address

    [Business​Entity​Address!](https://shopify.dev/docs/api/admin-graphql/latest/objects/BusinessEntityAddress)

    non-null

    The address of the merchant's Business Entity.

  * archived

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the Business Entity is archived from the shop.

  * company​Name

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The name of the company associated with the merchant's Business Entity.

  * display​Name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The display name of the merchant's Business Entity.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * primary

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether it's the merchant's primary Business Entity.

  * shopify​Payments​Account

    [Shopify​Payments​Account](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsAccount)

    Returns the Shopify Payments account information for the shop. Includes current balances across all currencies, payout schedules, and bank account configurations.

    The account includes [`ShopifyPaymentsBalanceTransaction`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsBalanceTransaction) records showing charges, refunds, and adjustments that affect your balance. Also includes [`ShopifyPaymentsDispute`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsDispute) records and [`ShopifyPaymentsPayout`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsPayout) history between the account and connected [`ShopifyPaymentsBankAccount`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsBankAccount) configurations.

***

## Examples

* ### businessEntities reference
