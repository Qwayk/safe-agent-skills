---
title: financeAppAccessPolicy - GraphQL Admin
description: Returns the access policy for a finance app .
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/financeAppAccessPolicy
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/financeAppAccessPolicy.md
---

# finance​App​Access​Policy

query

Requires User session and api client must be valid.

Returns the access policy for a finance app .

## Possible returns

* Finance​App​Access​Policy

  [Finance​App​Access​Policy!](https://shopify.dev/docs/api/admin-graphql/latest/objects/FinanceAppAccessPolicy)

  Current user's access policy for a finance app.

  * access

    [\[Banking​Finance​App​Access!\]!](https://shopify.dev/docs/api/admin-graphql/latest/enums/BankingFinanceAppAccess)

    non-null

    Current shop staff's access within the app.

***

## Examples

* ### financeAppAccessPolicy reference
