---
title: taxonomy - GraphQL Admin
description: >-
  Access to Shopify's [standardized product
  taxonomy](https://shopify.github.io/product-taxonomy/releases/unstable/?categoryId=sg-4-17-2-17)
  for categorizing products. The
  [`Taxonomy`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Taxonomy)
  organizes products into a hierarchical tree structure with categories,
  attributes, and values.


  Query categories using search terms, or navigate the hierarchy by requesting
  children, siblings, or descendants of specific categories. Each
  [`TaxonomyCategory`](https://shopify.dev/docs/api/admin-graphql/latest/objects/TaxonomyCategory)
  includes its position in the tree, parent-child relationships, and associated
  attributes for that product category.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/taxonomy'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/taxonomy.md'
---

# taxonomy

query

Access to Shopify's [standardized product taxonomy](https://shopify.github.io/product-taxonomy/releases/unstable/?categoryId=sg-4-17-2-17) for categorizing products. The [`Taxonomy`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Taxonomy) organizes products into a hierarchical tree structure with categories, attributes, and values.

Query categories using search terms, or navigate the hierarchy by requesting children, siblings, or descendants of specific categories. Each [`TaxonomyCategory`](https://shopify.dev/docs/api/admin-graphql/latest/objects/TaxonomyCategory) includes its position in the tree, parent-child relationships, and associated attributes for that product category.

## Possible returns

* Taxonomy

  [Taxonomy](https://shopify.dev/docs/api/admin-graphql/latest/objects/Taxonomy)

  Represents Shopify's [standardized product taxonomy](https://shopify.github.io/product-taxonomy/releases/unstable/?categoryId=sg-4-17-2-17) tree. Provides categories that you can filter by search criteria or hierarchical relationships.

  You can search categories globally, retrieve children of a specific category, find siblings, or get descendants. When you specify no filter arguments, you get all top-level categories in the taxonomy.

  * categories

    [Taxonomy​Category​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/TaxonomyCategoryConnection)

    non-null

    Returns the categories of the product taxonomy based on the arguments provided. If a `search` argument is provided, then all categories that match the search query globally are returned. If a `children_of` argument is provided, then all children of the specified category are returned. If a `siblings_of` argument is provided, then all siblings of the specified category are returned. If a `decendents_of` argument is provided, then all descendents of the specified category are returned. If no arguments are provided, then all the top-level categories of the taxonomy are returned.

    * search

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      ### Arguments

      Searches the product taxonomy for matching categories.

    * children​Of

      [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      The ID of the category associated with the child categories to return.

    * siblings​Of

      [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      The ID of the category associated with the sibling categories to return.

    * descendants​Of

      [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      The ID of the category associated with the descendant categories to return.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

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

    ***

***

## Examples

* ### taxonomy reference
