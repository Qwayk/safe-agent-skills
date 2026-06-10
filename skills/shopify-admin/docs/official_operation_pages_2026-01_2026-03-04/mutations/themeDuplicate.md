---
title: themeDuplicate - GraphQL Admin
description: Duplicates a theme.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/themeDuplicate'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/themeDuplicate.md
---

# theme​Duplicate

mutation

Requires The user needs write\_themes and an exemption from Shopify to modify themes. If you think that your app is eligible for an exemption and should have access to this API, then you can [submit an exception request](https://docs.google.com/forms/d/e/1FAIpQLSfZTB1vxFC5d1-GPdqYunWRGUoDcOheHQzfK2RoEFEHrknt5g/viewform).

Duplicates a theme.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  ID of the theme to be duplicated.

* name

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  Name of the new theme.

***

## Theme​Duplicate​Payload returns

* new​Theme

  [Online​Store​Theme](https://shopify.dev/docs/api/admin-graphql/latest/objects/OnlineStoreTheme)

  The newly duplicated theme.

* user​Errors

  [\[Theme​Duplicate​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ThemeDuplicateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### themeDuplicate reference
