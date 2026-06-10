---
title: productDuplicateJob - GraphQL Admin
description: Returns the product duplicate job.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/productDuplicateJob
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/productDuplicateJob.md
---

# product​Duplicate​Job

query

Returns the product duplicate job.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  An ID of a product duplicate job to fetch.

***

## Possible returns

* Product​Duplicate​Job

  [Product​Duplicate​Job!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductDuplicateJob)

  Represents a product duplication job.

  * done

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    This indicates if the job is still queued or has been run.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID that's returned when running an asynchronous mutation.

***

## Examples

* ### productDuplicateJob reference
