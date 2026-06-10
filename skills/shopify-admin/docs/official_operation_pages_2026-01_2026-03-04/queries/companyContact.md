---
title: companyContact - GraphQL Admin
description: Returns a `CompanyContact` resource by ID.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/companyContact'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/companyContact.md'
---

# company​Contact

query

Returns a `CompanyContact` resource by ID.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the `CompanyContact` to return.

***

## Possible returns

* Company​Contact

  [Company​Contact](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyContact)

  A person who acts on behalf of a [`Company`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Company) to make B2B purchases. Company contacts are associated with [`Customer`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer) accounts and can place orders on behalf of their company.

  Each contact can be assigned to one or more [`CompanyLocation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyLocation) objects with specific roles that determine their permissions and access to catalogs, pricing, and payment terms configured for those locations.

  * company

    [Company!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Company)

    non-null

    The company to which the contact belongs.

  * created​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time ([ISO 8601 format](http://en.wikipedia.org/wiki/ISO_8601)) at which the company contact was created at Shopify.

  * customer

    [Customer!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)

    non-null

    The customer associated to this contact.

  * draft​Orders

    [Draft​Order​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/DraftOrderConnection)

    non-null

    The list of draft orders for the company contact.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * last

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * before

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * reverse

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Reverse the order of the underlying list.

    * sort​Key

      [Draft​Order​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/DraftOrderSortKeys)

      Default:ID

      Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

    * query

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

      * * default

          string

        * created\_at

          time

        - Filter by a case-insensitive search of multiple fields in a document.

        - Example:
          * `query=Bob Norman`
          * `query=title:green hoodie`

      * customer\_id

        id

      * * id

          id

        * source

          string

        - Filter by `id` range.

        - Example:
          * `id:1234`
          * `id:>=1234`
          * `id:<=1234`

      * status

        string

      * tag

        string

      * updated\_at

        time

    ***

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * is​Main​Contact

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the contact is the main contact of the company.

  * lifetime​Duration

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The lifetime duration of the company contact, since its creation date on Shopify. Examples: `1 year`, `2 months`, `3 days`.

  * locale

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The company contact's locale (language).

  * orders

    [Order​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/OrderConnection)

    non-null

    The list of orders for the company contact.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * last

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * before

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * reverse

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Reverse the order of the underlying list.

    * sort​Key

      [Order​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/OrderSortKeys)

      Default:ID

      Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

    ***

  * role​Assignments

    [Company​Contact​Role​Assignment​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/CompanyContactRoleAssignmentConnection)

    non-null

    The list of roles assigned to this company contact.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * last

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * before

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * reverse

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Reverse the order of the underlying list.

    * sort​Key

      [Company​Contact​Role​Assignment​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/CompanyContactRoleAssignmentSortKeys)

      Default:ID

      Sort the underlying list by the given key.

    * query

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

      * * default

          string

        * company\_contact\_id

          id

        - Filter by a case-insensitive search of multiple fields in a document.

        - Example:
          * `query=Bob Norman`
          * `query=title:green hoodie`

      * company\_contact\_role\_id

        id

      * company\_id

        id

      * company\_location\_id

        id

      * created\_at

        time

      * * id

          id

        * location\_name

          string

        - Filter by `id` range.

        - Example:
          * `id:1234`
          * `id:>=1234`
          * `id:<=1234`

      * role\_name

        string

      * updated\_at

        time

    ***

  * title

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The company contact's job title.

  * updated​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time ([ISO 8601 format](http://en.wikipedia.org/wiki/ISO_8601)) at which the company contact was last updated.

***

## Examples

* ### companyContact reference
