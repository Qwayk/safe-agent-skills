---
title: urlRedirectImportSubmit - GraphQL Admin
description: >-
  Submits a `UrlRedirectImport` request to be processed.


  The `UrlRedirectImport` request is first created with the
  [`urlRedirectImportCreate`](https://shopify.dev/api/admin-graphql/latest/mutations/urlRedirectImportCreate)
  mutation.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/urlRedirectImportSubmit
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/urlRedirectImportSubmit.md
---

# url​Redirect​Import​Submit

mutation

Requires `write_online_store_navigation` access scope.

Submits a `UrlRedirectImport` request to be processed.

The `UrlRedirectImport` request is first created with the [`urlRedirectImportCreate`](https://shopify.dev/api/admin-graphql/latest/mutations/urlRedirectImportCreate) mutation.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the [`UrlRedirectImport`](https://shopify.dev/api/admin-graphql/latest/objects/UrlRedirectImport) object.

***

## Url​Redirect​Import​Submit​Payload returns

* job

  [Job](https://shopify.dev/docs/api/admin-graphql/latest/objects/Job)

  The asynchronous job importing the redirects.

* user​Errors

  [\[Url​Redirect​Import​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UrlRedirectImportUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### urlRedirectImportSubmit reference
