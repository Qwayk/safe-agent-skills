---
title: marketLocalizableResource - GraphQL Admin
description: A resource that can have localized values for different markets.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/marketLocalizableResource
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/marketLocalizableResource.md
---

# market​Localizable​Resource

query

Requires `read_translations` access scope.

A resource that can have localized values for different markets.

## Arguments

* resource​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  Find a market localizable resource by ID.

***

## Possible returns

* Market​Localizable​Resource

  [Market​Localizable​Resource](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketLocalizableResource)

  A resource that has market localizable fields.

  * market​Localizable​Content

    [\[Market​Localizable​Content!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketLocalizableContent)

    non-null

    The market localizable content.

  * market​Localizations

    [\[Market​Localization!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketLocalization)

    non-null

    Market localizations for the market localizable content.

    * market​Id

      [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      required

      ### Arguments

      Filters market localizations by market ID.

    ***

  * resource​Id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    The GID of the resource.

***

## Examples

* ### marketLocalizableResource reference
