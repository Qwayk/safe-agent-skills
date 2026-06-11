---
title: segment - GraphQL Admin
description: >-
  Retrieves a customer
  [`Segment`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Segment)
  by ID. Segments are dynamic groups of customers that meet specific criteria
  defined through [ShopifyQL
  queries](https://shopify.dev/docs/api/shopifyql/segment-query-language-reference).


  Use segments for targeted marketing campaigns, analyzing customer behavior, or
  creating personalized experiences. Each segment includes its name, creation
  date, and the query that defines which
  [`Customer`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)
  objects belong to it.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/segment'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/segment.md'
---

# segment

query

Retrieves a customer [`Segment`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Segment) by ID. Segments are dynamic groups of customers that meet specific criteria defined through [ShopifyQL queries](https://shopify.dev/docs/api/shopifyql/segment-query-language-reference).

Use segments for targeted marketing campaigns, analyzing customer behavior, or creating personalized experiences. Each segment includes its name, creation date, and the query that defines which [`Customer`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer) objects belong to it.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  Find a segment by ID.

***

## Possible returns

* Segment

  [Segment](https://shopify.dev/docs/api/admin-graphql/latest/objects/Segment)

  A group of [customers](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer) that meet specific criteria defined through [ShopifyQL query](https://shopify.dev/docs/api/shopifyql/segment-query-language-reference) conditions. Common use cases for segments include customer analytics, targeted marketing campaigns, and automated discount eligibility.

  The segment's [`query`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Segment#field-query) field contains ShopifyQL conditions that determine membership, such as purchase history, location, or engagement patterns. Tracks when the segment was created with [`creationDate`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Segment#field-creationDate) and when it was last modified with [`lastEditDate`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Segment#field-lastEditDate).

  * creation​Date

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the segment was added to the store.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * last​Edit​Date

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the segment was last updated.

  * name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The name of the segment.

  * query

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    A precise definition of the segment. The definition is composed of a combination of conditions on facts about customers.

***

## Examples

* ### segment reference
