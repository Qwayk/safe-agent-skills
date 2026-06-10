---
title: companyLocationUpdate - GraphQL Admin
description: >-
  Updates a company location's information and B2B checkout settings. Company
  locations are branches or offices where
  [`CompanyContact`](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyContact)
  members place orders on behalf of the company. Contacts must be assigned to a
  location through `roleAssignments` to place orders.


  The mutation modifies details such as the location's name, contact
  information, preferred locale, and internal notes. You can also configure the
  B2B checkout experience through
  [`BuyerExperienceConfiguration`](https://shopify.dev/docs/api/admin-graphql/latest/objects/BuyerExperienceConfiguration)
  settings that control whether orders require merchant review,
  [`PaymentTermsTemplate`](https://shopify.dev/docs/api/admin-graphql/latest/objects/PaymentTermsTemplate)
  settings, shipping address editing permissions, and
  [`DepositConfiguration`](https://shopify.dev/docs/api/admin-graphql/latest/unions/DepositConfiguration)
  requirements.


  Learn more about [managing company
  locations](https://shopify.dev/docs/apps/build/b2b/manage-client-company-locations).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/companyLocationUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/companyLocationUpdate.md
---

# company​Location​Update

mutation

Requires `write_customers` access scope or `write_companies` access scope. Also: The API client must be installed on a Shopify Plus store.

Updates a company location's information and B2B checkout settings. Company locations are branches or offices where [`CompanyContact`](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyContact) members place orders on behalf of the company. Contacts must be assigned to a location through `roleAssignments` to place orders.

The mutation modifies details such as the location's name, contact information, preferred locale, and internal notes. You can also configure the B2B checkout experience through [`BuyerExperienceConfiguration`](https://shopify.dev/docs/api/admin-graphql/latest/objects/BuyerExperienceConfiguration) settings that control whether orders require merchant review, [`PaymentTermsTemplate`](https://shopify.dev/docs/api/admin-graphql/latest/objects/PaymentTermsTemplate) settings, shipping address editing permissions, and [`DepositConfiguration`](https://shopify.dev/docs/api/admin-graphql/latest/unions/DepositConfiguration) requirements.

Learn more about [managing company locations](https://shopify.dev/docs/apps/build/b2b/manage-client-company-locations).

## Arguments

* company​Location​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the company location to update.

* input

  [Company​Location​Update​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CompanyLocationUpdateInput)

  required

  The input fields to update in the company location.

***

## Company​Location​Update​Payload returns

* company​Location

  [Company​Location](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyLocation)

  The updated company location.

* user​Errors

  [\[Business​Customer​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/BusinessCustomerUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### companyLocationUpdate reference
