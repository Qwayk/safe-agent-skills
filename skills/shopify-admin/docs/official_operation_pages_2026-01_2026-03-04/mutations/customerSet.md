---
title: customerSet - GraphQL Admin
description: >-
  Creates or updates a customer in a single mutation.


  Use this mutation when syncing information from an external data source into
  Shopify.


  This mutation can be used to create a new customer, update an existing
  customer by id, or

  upsert a customer by a unique key (email or phone).


  To create a new customer omit the `identifier` argument.

  To update an existing customer, include the `identifier` with the id of the
  customer to update.


  To perform an 'upsert' by unique key (email or phone)

  use the `identifier` argument to upsert a customer by a unique key (email or
  phone). If a customer

  with the specified unique key exists, it will be updated. If not, a new
  customer will be created with

  that unique key.


  As of API version 2022-10, apps using protected customer data must meet the

  protected customer data
  [requirements](https://shopify.dev/apps/store/data-protection/protected-customer-data)


  Any list field (e.g.

  [addresses](https://shopify.dev/api/admin-graphql/unstable/input-objects/MailingAddressInput),

  will be updated so that all included entries are either created or updated,
  and all existing entries not

  included will be deleted.


  All other fields will be updated to the value passed. Omitted fields will not
  be updated.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerSet'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerSet.md'
---

# customer​Set

mutation

Requires `write_customers` access scope.

Creates or updates a customer in a single mutation.

Use this mutation when syncing information from an external data source into Shopify.

This mutation can be used to create a new customer, update an existing customer by id, or upsert a customer by a unique key (email or phone).

To create a new customer omit the `identifier` argument. To update an existing customer, include the `identifier` with the id of the customer to update.

To perform an 'upsert' by unique key (email or phone) use the `identifier` argument to upsert a customer by a unique key (email or phone). If a customer with the specified unique key exists, it will be updated. If not, a new customer will be created with that unique key.

As of API version 2022-10, apps using protected customer data must meet the protected customer data [requirements](https://shopify.dev/apps/store/data-protection/protected-customer-data)

Any list field (e.g. [addresses](https://shopify.dev/api/admin-graphql/unstable/input-objects/MailingAddressInput), will be updated so that all included entries are either created or updated, and all existing entries not included will be deleted.

All other fields will be updated to the value passed. Omitted fields will not be updated.

## Arguments

* identifier

  [Customer​Set​Identifiers](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CustomerSetIdentifiers)

  Specifies the identifier that will be used to lookup the resource.

* input

  [Customer​Set​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CustomerSetInput)

  required

  The properties of the customer.

***

## Customer​Set​Payload returns

* customer

  [Customer](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)

  The created or updated customer.

* user​Errors

  [\[Customer​Set​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CustomerSetUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### customerSet reference
