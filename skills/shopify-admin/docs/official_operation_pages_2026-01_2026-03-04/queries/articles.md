---
title: articles - GraphQL Admin
description: >-
  Returns a paginated list of articles from the shop's blogs.
  [`Article`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Article)
  objects are blog posts that contain content like text, images, and tags.


  Supports [cursor-based
  pagination](https://shopify.dev/docs/api/usage/pagination-graphql) to control
  the number of articles returned and their order. Use the
  [`query`](https://shopify.dev/docs/api/admin-graphql/latest/queries/articles#arguments-query)
  argument to filter results by specific criteria.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/articles'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/articles.md'
---

# articles

query

Returns a paginated list of articles from the shop's blogs. [`Article`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Article) objects are blog posts that contain content like text, images, and tags.

Supports [cursor-based pagination](https://shopify.dev/docs/api/usage/pagination-graphql) to control the number of articles returned and their order. Use the [`query`](https://shopify.dev/docs/api/admin-graphql/latest/queries/articles#arguments-query) argument to filter results by specific criteria.

## ArticleConnection arguments

[ArticleConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ArticleConnection)

* after

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* before

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* first

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* last

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* query

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

  * * default

      string

    * author

      string

    - Filter by a case-insensitive search of multiple fields in a document.

    - Example:

      * `query=Bob Norman`
      * `query=handle:summer-collection-announcement`

      Filter by the author of the article.

  * * blog\_id

      string

    * blog\_title

      string

    - Filter by the ID of the blog the article belongs to.

    - Example:
      * `blog_id:1234`
      * `blog_id:>=1234`
      * `blog_id:<=1234`

  * * created\_at

      time

    * handle

      string

    * id

      id

    * published\_at

      time

    * published\_status

      string

    - Filter by the date and time when the article was created.

    - Example:

      * `created_at:>'2020-10-21T23:39:20Z'`
      * `created_at:<now`
      * `created_at:<=2024`

      Filter by the article's handle.

    - Example:

      * `handle:summer-collection-announcement`
      * `handle:how-to-guide`

      Filter by `id` range.

    - Example:

      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

      Filter by the date and time when the article was published.

    - Example:

      * `published_at:>'2020-10-21T23:39:20Z'`
      * `published_at:<now`
      * `published_at:<=2024`

      Filter by published status

  * * tag

      string

    * tag\_not

      string

    * title

      string

    * updated\_at

      time

    - Filter objects by the `tag` field.

    - Example:

      * `tag:my_tag`

      Filter by objects that don’t have the specified tag.

    - Example:

      * `tag_not:my_tag`

      Filter by the title of the article.

    - Example:

      * `title:summer-collection`
      * `title:green hoodie`

      Filter by the date and time when the article was last updated.

      Example:

      * `updated_at:>'2020-10-21T23:39:20Z'`
      * `updated_at:<now`
      * `updated_at:<=2024`

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* sort​Key

  [Article​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/ArticleSortKeys)

  Default:ID

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Article​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ArticleEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Article!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Article)

  non-null

  A list of nodes that are contained in ArticleEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### articles reference
