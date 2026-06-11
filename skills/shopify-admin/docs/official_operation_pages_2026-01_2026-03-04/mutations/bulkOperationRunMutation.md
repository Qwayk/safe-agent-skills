---
title: bulkOperationRunMutation - GraphQL Admin
description: >-
  Creates and runs a [bulk
  operation](https://shopify.dev/docs/api/admin-graphql/latest/objects/BulkOperation)
  to import data asynchronously. This mutation executes a specified GraphQL
  mutation multiple times using input data from a [JSONL](http://jsonlines.org/)
  file that you've uploaded to Shopify.


  The operation processes each line in your JSONL file as a separate mutation
  execution. The operation delivers results in a JSONL file when it completes.
  You can run one bulk mutation operation at a time per shop, though a
  [`bulkOperationRunQuery`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/bulkoperationrunquery)
  operation can run simultaneously.


  Learn more about [bulk importing
  data](https://shopify.dev/docs/api/usage/bulk-operations/imports).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/bulkOperationRunMutation
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/bulkOperationRunMutation.md
---

# bulk​Operation​Run​Mutation

mutation

Requires Only accessible by supported access tokens: <https://shopify.dev/docs/api/usage/bulk-operations/queries#access-token-considerations>.

Creates and runs a [bulk operation](https://shopify.dev/docs/api/admin-graphql/latest/objects/BulkOperation) to import data asynchronously. This mutation executes a specified GraphQL mutation multiple times using input data from a [JSONL](http://jsonlines.org/) file that you've uploaded to Shopify.

The operation processes each line in your JSONL file as a separate mutation execution. The operation delivers results in a JSONL file when it completes. You can run one bulk mutation operation at a time per shop, though a [`bulkOperationRunQuery`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/bulkoperationrunquery) operation can run simultaneously.

Learn more about [bulk importing data](https://shopify.dev/docs/api/usage/bulk-operations/imports).

## Arguments

* client​Identifier

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  An optional identifier which may be used for querying.

* mutation

  [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  The mutation to be executed in bulk.

* staged​Upload​Path

  [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  The staged upload path of the file containing mutation variables.

* group​Objects

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  DeprecatedDefault:true

***

## Bulk​Operation​Run​Mutation​Payload returns

* bulk​Operation

  [Bulk​Operation](https://shopify.dev/docs/api/admin-graphql/latest/objects/BulkOperation)

  The newly created bulk operation.

* user​Errors

  [\[Bulk​Mutation​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/BulkMutationUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### bulkOperationRunMutation reference
