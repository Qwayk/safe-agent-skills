---
title: consentPolicyUpdate - GraphQL Admin
description: Update or create consent policies in bulk.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/consentPolicyUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/consentPolicyUpdate.md
---

# consent​Policy​Update

mutation

Requires `write_privacy_settings` access scope.

Update or create consent policies in bulk.

## Arguments

* consent​Policies

  [\[Consent​Policy​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ConsentPolicyInput)

  required

  The consent policies to update or create. If the country and region matches an existing consent policy, then the consent policy is updated. Otherwise, a new consent policy is created.

***

## Consent​Policy​Update​Payload returns

* updated​Policies

  [\[Consent​Policy!\]](https://shopify.dev/docs/api/admin-graphql/latest/objects/ConsentPolicy)

  All updated and created consent policies. The consent policies that haven't been modified as part of the mutation aren't returned.

* user​Errors

  [\[Consent​Policy​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ConsentPolicyError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### consentPolicyUpdate reference
