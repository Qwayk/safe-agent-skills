---
title: currentStaffMember - GraphQL Admin
description: The staff member making the API request.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/currentStaffMember'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/currentStaffMember.md
---

# current​Staff​Member

query

The staff member making the API request.

## Possible returns

* Staff​Member

  [Staff​Member](https://shopify.dev/docs/api/admin-graphql/latest/objects/StaffMember)

  A user account that can access the Shopify admin to manage store operations. Includes personal information and account status.

  You can assign staff members to [`CompanyLocation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyLocation) objects for [B2B operations](https://shopify.dev/docs/apps/build/b2b), limiting their actions to those locations.

  * account​Type

    [Account​Type](https://shopify.dev/docs/api/admin-graphql/latest/enums/AccountType)

    The type of account the staff member has.

  * active

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the staff member is active.

  * avatar

    [Image!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Image)

    non-null

    The image used as the staff member's avatar in the Shopify admin.

    * max​Width

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      Deprecated

      ### Arguments

    * max​Height

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      Deprecated

    * fallback

      [Staff​Member​Default​Image](https://shopify.dev/docs/api/admin-graphql/latest/enums/StaffMemberDefaultImage)

      Default:DEFAULT

      The default image returned if the staff member has no avatar.

    ***

  * email

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The staff member's email address.

  * exists

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the staff member's account exists.

  * first​Name

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The staff member's first name.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * initials

    [\[String!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The staff member's initials, if available.

  * is​Shop​Owner

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the staff member is the shop owner.

  * last​Name

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The staff member's last name.

  * locale

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The staff member's preferred locale. Locale values use the format `language` or `language-COUNTRY`, where `language` is a two-letter language code, and `COUNTRY` is a two-letter country code. For example: `en` or `en-US`

  * name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The staff member's full name.

  * phone

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The staff member's phone number.

  * private​Data

    [Staff​Member​Private​Data!](https://shopify.dev/docs/api/admin-graphql/latest/objects/StaffMemberPrivateData)

    non-null

    The data used to customize the Shopify admin experience for the staff member.

***

## Examples

* ### currentStaffMember reference
