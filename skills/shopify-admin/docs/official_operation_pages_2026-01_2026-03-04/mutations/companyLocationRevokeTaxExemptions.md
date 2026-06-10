---
title: companyLocationRevokeTaxExemptions - GraphQL Admin
description: Revokes tax exemptions from the company location.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/companyLocationRevokeTaxExemptions
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/companyLocationRevokeTaxExemptions.md
---

# company​Location​Revoke​Tax​Exemptions

mutation

Requires `write_customers` access scope or `write_companies` access scope. Also: The API client must be installed on a Shopify Plus store.

Deprecated. Use [companyLocationTaxSettingsUpdate](https://shopify.dev/docs/api/admin-graphql/latest/mutations/companyLocationTaxSettingsUpdate) instead.

Revokes tax exemptions from the company location.

## Arguments

* company​Location​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The location from which the tax exemptions will be revoked.

* tax​Exemptions

  [\[Tax​Exemption!\]!](https://shopify.dev/docs/api/admin-graphql/latest/enums/TaxExemption)

  required

  The tax exemptions that are being revoked from the location.

***

## Company​Location​Revoke​Tax​Exemptions​Payload returns

* company​Location

  [Company​Location](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyLocation)

  The updated company location.

* user​Errors

  [\[Business​Customer​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/BusinessCustomerUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### companyLocationRevokeTaxExemptions reference
