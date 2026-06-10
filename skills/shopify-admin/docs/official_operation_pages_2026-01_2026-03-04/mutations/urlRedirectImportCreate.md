---
title: urlRedirectImportCreate - GraphQL Admin
description: >-
  Creates a
  [`UrlRedirectImport`](https://shopify.dev/api/admin-graphql/latest/objects/UrlRedirectImport)
  object.


  After creating the `UrlRedirectImport` object, the `UrlRedirectImport` request
  can be performed using the
  [`urlRedirectImportSubmit`](https://shopify.dev/api/admin-graphql/latest/mutations/urlRedirectImportSubmit)
  mutation.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/urlRedirectImportCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/urlRedirectImportCreate.md
---

# url​Redirect​Import​Create

mutation

Requires `write_online_store_navigation` access scope.

Creates a [`UrlRedirectImport`](https://shopify.dev/api/admin-graphql/latest/objects/UrlRedirectImport) object.

After creating the `UrlRedirectImport` object, the `UrlRedirectImport` request can be performed using the [`urlRedirectImportSubmit`](https://shopify.dev/api/admin-graphql/latest/mutations/urlRedirectImportSubmit) mutation.

## Arguments

* url

  [URL!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

  required

  The staged upload URL of the CSV file. You can download [a sample URL redirect CSV file](https://help.shopify.com/csv/sample-redirect-template.csv).

***

## Url​Redirect​Import​Create​Payload returns

* url​Redirect​Import

  [Url​Redirect​Import](https://shopify.dev/docs/api/admin-graphql/latest/objects/UrlRedirectImport)

  The created `URLRedirectImport` object.

* user​Errors

  [\[Url​Redirect​Import​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UrlRedirectImportUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### urlRedirectImportCreate reference
