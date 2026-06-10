---
title: marketLocalizationsRegister - GraphQL Admin
description: Creates or updates market localizations.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketLocalizationsRegister
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketLocalizationsRegister.md
---

# market​Localizations​Register

mutation

Requires `write_translations` access scope.

Creates or updates market localizations.

## Arguments

* market​Localizations

  [\[Market​Localization​Register​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MarketLocalizationRegisterInput)

  required

  The input fields for a market localization.

* resource​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the resource that is being localized within the context of a market.

***

## Market​Localizations​Register​Payload returns

* market​Localizations

  [\[Market​Localization!\]](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketLocalization)

  The market localizations that were created or updated.

* user​Errors

  [\[Translation​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/TranslationUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### marketLocalizationsRegister reference
