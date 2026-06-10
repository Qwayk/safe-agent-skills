---
title: companyLocationRevokeTaxRegistration - GraphQL Admin
description: Revokes tax registration on a company location.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/companyLocationRevokeTaxRegistration
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/companyLocationRevokeTaxRegistration.md
---

# company​Location​Revoke​Tax​Registration

mutation

Requires `write_customers` access scope or `write_companies` access scope. Also: The API client must be installed on a Shopify Plus store.

Deprecated. Use [companyLocationTaxSettingsUpdate](https://shopify.dev/docs/api/admin-graphql/latest/mutations/companyLocationTaxSettingsUpdate) instead.

Revokes tax registration on a company location.

## Arguments

* company​Location​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The location whose tax registration is being revoked.

***

## Company​Location​Revoke​Tax​Registration​Payload returns

* company​Location

  [Company​Location](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyLocation)

  The updated company location.

* user​Errors

  [\[Business​Customer​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/BusinessCustomerUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### companyLocationRevokeTaxRegistration reference
