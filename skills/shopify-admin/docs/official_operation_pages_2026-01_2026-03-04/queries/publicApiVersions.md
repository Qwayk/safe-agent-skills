---
title: publicApiVersions - GraphQL Admin
description: >-
  The list of publicly-accessible Admin API versions, including supported
  versions, the release candidate, and unstable versions.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/publicApiVersions'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/publicApiVersions.md
---

# public​Api​Versions

query

The list of publicly-accessible Admin API versions, including supported versions, the release candidate, and unstable versions.

## Possible returns

* Api​Version

  [\[Api​Version!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ApiVersion)

  A version of the API, as defined by [Shopify API versioning](https://shopify.dev/api/usage/versioning). Versions are commonly referred to by their handle (for example, `2021-10`).

  * display​Name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The human-readable name of the version.

  * handle

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The unique identifier of an ApiVersion. All supported API versions have a date-based (YYYY-MM) or `unstable` handle.

  * supported

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the version is actively supported by Shopify. Supported API versions are guaranteed to be stable. Unsupported API versions include unstable, release candidate, and end-of-life versions that are marked as unsupported. For more information, refer to [Versioning](https://shopify.dev/api/usage/versioning).

***

## Examples

* ### publicApiVersions reference
