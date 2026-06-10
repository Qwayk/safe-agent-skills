---
title: urlRedirectImport - GraphQL Admin
description: Returns a `UrlRedirectImport` resource by ID.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/urlRedirectImport'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/urlRedirectImport.md
---

# url​Redirect​Import

query

Returns a `UrlRedirectImport` resource by ID.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the `UrlRedirectImport` to return.

***

## Possible returns

* Url​Redirect​Import

  [Url​Redirect​Import](https://shopify.dev/docs/api/admin-graphql/latest/objects/UrlRedirectImport)

  A request to import a [`URLRedirect`](https://shopify.dev/api/admin-graphql/latest/objects/UrlRedirect) object into the Online Store channel. Apps can use this to query the state of an `UrlRedirectImport` request.

  For more information, see [`url-redirect`](https://help.shopify.com/en/manual/online-store/menus-and-links/url-redirect)s.

  * count

    [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    The number of rows in the file.

  * created​Count

    [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    The number of redirects created from the import.

  * failed​Count

    [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    The number of redirects that failed to be imported.

  * finished

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the import is finished.

  * finished​At

    [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    The date and time when the import finished.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    The ID of the `UrlRedirectImport` object.

  * preview​Redirects

    [\[Url​Redirect​Import​Preview!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UrlRedirectImportPreview)

    non-null

    A list of up to three previews of the URL redirects to be imported.

  * updated​Count

    [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    The number of redirects updated during the import.

***

## Examples

* ### urlRedirectImport reference
