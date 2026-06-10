---
title: collectionCreate - GraphQL Admin
description: >-
  Creates a
  [collection](https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection)

  to group
  [products](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)
  together

  in the [online store](https://shopify.dev/docs/apps/build/online-store) and

  other [sales channels](https://shopify.dev/docs/apps/build/sales-channels).

  For example, an athletics store might create different collections for running
  attire, shoes, and accessories.


  There are two types of collections:


  - **[Custom (manual)
  collections](https://help.shopify.com/manual/products/collections/manual-shopify-collection)**:
  You specify the products to include in a collection.

  - **[Smart (automated)
  collections](https://help.shopify.com/manual/products/collections/automated-collections)**:
  You define rules, and products matching those rules are automatically

  included in the collection.


  Use the `collectionCreate` mutation when you need to:


  - Create a new collection for a product launch or campaign

  - Organize products by category, season, or promotion

  - Automate product grouping using rules (for example, by tag, type, or price)


  > Note:

  > The created collection is unpublished by default. To make it available to
  customers,

  use the
  [`publishablePublish`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/publishablePublish)

  mutation after creation.


  Learn more about [using metafields with smart
  collections](https://shopify.dev/docs/apps/build/custom-data/metafields/use-metafield-capabilities).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionCreate'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionCreate.md
---

# collection​Create

mutation

Requires `write_products` access scope. Also: The app must have access to the input fields used to create the collection. Further, the store must not be on the Starter or Retail plans and user must have a permission to create collection.

Creates a [collection](https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection) to group [products](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product) together in the [online store](https://shopify.dev/docs/apps/build/online-store) and other [sales channels](https://shopify.dev/docs/apps/build/sales-channels). For example, an athletics store might create different collections for running attire, shoes, and accessories.

There are two types of collections:

* **[Custom (manual) collections](https://help.shopify.com/manual/products/collections/manual-shopify-collection)**: You specify the products to include in a collection.
* **[Smart (automated) collections](https://help.shopify.com/manual/products/collections/automated-collections)**: You define rules, and products matching those rules are automatically included in the collection.

Use the `collectionCreate` mutation when you need to:

* Create a new collection for a product launch or campaign
* Organize products by category, season, or promotion
* Automate product grouping using rules (for example, by tag, type, or price)

***

**Note:** The created collection is unpublished by default. To make it available to customers, use the \<a href="https://shopify.dev/docs/api/admin-graphql/latest/mutations/publishablePublish">\<code>\<span class="PreventFireFoxApplyingGapToWBR">publishable\<wbr/>Publish\</span>\</code>\</a> mutation after creation.

***

Learn more about [using metafields with smart collections](https://shopify.dev/docs/apps/build/custom-data/metafields/use-metafield-capabilities).

## Arguments

* input

  [Collection​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CollectionInput)

  required

  The properties to use when creating the collection.

***

## Collection​Create​Payload returns

* collection

  [Collection](https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection)

  The collection that has been created.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a collection with an image

  #### Description

  Create a collection that includes an image. This example shows how to attach image details, such as the source URL and alt text during the process of creating the collection. The response returns the collection's ID, title, and other specified image details.

  #### Query

  ```graphql
  mutation CollectionCreate($input: CollectionInput!) {
    collectionCreate(input: $input) {
      userErrors {
        field
        message
      }
      collection {
        id
        title
        image {
          url
          altText
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "title": "Collection with Image",
      "image": {
        "src": "tmp/26371970/collections/e36e8f91-08a6-46f0-8db7-dd37a55ccd57/test_file",
        "altText": "A beautiful collection image"
      }
    }
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation CollectionCreate($input: CollectionInput!) { collectionCreate(input: $input) { userErrors { field message } collection { id title image { url altText } } } }",
   "variables": {
      "input": {
        "title": "Collection with Image",
        "image": {
          "src": "tmp/26371970/collections/e36e8f91-08a6-46f0-8db7-dd37a55ccd57/test_file",
          "altText": "A beautiful collection image"
        }
      }
    }
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    mutation CollectionCreate($input: CollectionInput!) {
      collectionCreate(input: $input) {
        userErrors {
          field
          message
        }
        collection {
          id
          title
          image {
            url
            altText
          }
        }
      }
    }`,
    {
      variables: {
          "input": {
              "title": "Collection with Image",
              "image": {
                  "src": "tmp/26371970/collections/e36e8f91-08a6-46f0-8db7-dd37a55ccd57/test_file",
                  "altText": "A beautiful collection image"
              }
          }
      },
    },
    );
    const json = await response.json();
    return json.data;
  }
  ```

  #### Ruby

  ```ruby
  session = ShopifyAPI::Auth::Session.new(
    shop: "your-development-store.myshopify.com",
    access_token: access_token
  )
  client = ShopifyAPI::Clients::Graphql::Admin.new(
    session: session
  )

  query = <<~QUERY
    mutation CollectionCreate($input: CollectionInput!) {
      collectionCreate(input: $input) {
        userErrors {
          field
          message
        }
        collection {
          id
          title
          image {
            url
            altText
          }
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "title": "Collection with Image",
      "image": {
        "src": "tmp/26371970/collections/e36e8f91-08a6-46f0-8db7-dd37a55ccd57/test_file",
        "altText": "A beautiful collection image"
      }
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation CollectionCreate($input: CollectionInput!) {
        collectionCreate(input: $input) {
          userErrors {
            field
            message
          }
          collection {
            id
            title
            image {
              url
              altText
            }
          }
        }
      }`,
      "variables": {
          "input": {
              "title": "Collection with Image",
              "image": {
                  "src": "tmp/26371970/collections/e36e8f91-08a6-46f0-8db7-dd37a55ccd57/test_file",
                  "altText": "A beautiful collection image"
              }
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation CollectionCreate($input: CollectionInput!) {
    collectionCreate(input: $input) {
      userErrors {
        field
        message
      }
      collection {
        id
        title
        image {
          url
          altText
        }
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "title": "Collection with Image",
      "image": {
        "src": "tmp/26371970/collections/e36e8f91-08a6-46f0-8db7-dd37a55ccd57/test_file",
        "altText": "A beautiful collection image"
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "collectionCreate": {
      "userErrors": [],
      "collection": {
        "id": "gid://shopify/Collection/1063001313",
        "title": "Collection with Image",
        "image": {
          "url": "https://cdn.shopify.com/s/files/1/2637/1970/collections/test_file.jpg?v=1749673519",
          "altText": "A beautiful collection image"
        }
      }
    }
  }
  ```

* ### Create a custom collection

  #### Description

  Create a \[custom collection]\(https://help.shopify.com/manual/products/collections/manual-shopify-collection) by defining the collection's title, description, handle, and associated products. The response returns detailed information about the newly created collection, including its ID, title, description, update timestamp, handle, an image, and a list of associated products.

  #### Query

  ```graphql
  mutation CollectionCreate($input: CollectionInput!) {
    collectionCreate(input: $input) {
      collection {
        id
        title
        descriptionHtml
        updatedAt
        handle
        image {
          id
          height
          width
          url
        }
        products(first: 10) {
          nodes {
            id
            featuredMedia {
              id
            }
          }
        }
      }
      userErrors {
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "title": "New Custom Collection",
      "descriptionHtml": "This is a custom collection.",
      "handle": "custom-collection",
      "products": [
        "gid://shopify/Product/20995642"
      ]
    }
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation CollectionCreate($input: CollectionInput!) { collectionCreate(input: $input) { collection { id title descriptionHtml updatedAt handle image { id height width url } products(first: 10) { nodes { id featuredMedia { id } } } } userErrors { field message } } }",
   "variables": {
      "input": {
        "title": "New Custom Collection",
        "descriptionHtml": "This is a custom collection.",
        "handle": "custom-collection",
        "products": [
          "gid://shopify/Product/20995642"
        ]
      }
    }
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    mutation CollectionCreate($input: CollectionInput!) {
      collectionCreate(input: $input) {
        collection {
          id
          title
          descriptionHtml
          updatedAt
          handle
          image {
            id
            height
            width
            url
          }
          products(first: 10) {
            nodes {
              id
              featuredMedia {
                id
              }
            }
          }
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "input": {
              "title": "New Custom Collection",
              "descriptionHtml": "This is a custom collection.",
              "handle": "custom-collection",
              "products": [
                  "gid://shopify/Product/20995642"
              ]
          }
      },
    },
    );
    const json = await response.json();
    return json.data;
  }
  ```

  #### Ruby

  ```ruby
  session = ShopifyAPI::Auth::Session.new(
    shop: "your-development-store.myshopify.com",
    access_token: access_token
  )
  client = ShopifyAPI::Clients::Graphql::Admin.new(
    session: session
  )

  query = <<~QUERY
    mutation CollectionCreate($input: CollectionInput!) {
      collectionCreate(input: $input) {
        collection {
          id
          title
          descriptionHtml
          updatedAt
          handle
          image {
            id
            height
            width
            url
          }
          products(first: 10) {
            nodes {
              id
              featuredMedia {
                id
              }
            }
          }
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "title": "New Custom Collection",
      "descriptionHtml": "This is a custom collection.",
      "handle": "custom-collection",
      "products": [
        "gid://shopify/Product/20995642"
      ]
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation CollectionCreate($input: CollectionInput!) {
        collectionCreate(input: $input) {
          collection {
            id
            title
            descriptionHtml
            updatedAt
            handle
            image {
              id
              height
              width
              url
            }
            products(first: 10) {
              nodes {
                id
                featuredMedia {
                  id
                }
              }
            }
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "title": "New Custom Collection",
              "descriptionHtml": "This is a custom collection.",
              "handle": "custom-collection",
              "products": [
                  "gid://shopify/Product/20995642"
              ]
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation CollectionCreate($input: CollectionInput!) {
    collectionCreate(input: $input) {
      collection {
        id
        title
        descriptionHtml
        updatedAt
        handle
        image {
          id
          height
          width
          url
        }
        products(first: 10) {
          nodes {
            id
            featuredMedia {
              id
            }
          }
        }
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "title": "New Custom Collection",
      "descriptionHtml": "This is a custom collection.",
      "handle": "custom-collection",
      "products": [
        "gid://shopify/Product/20995642"
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "collectionCreate": {
      "collection": {
        "id": "gid://shopify/Collection/1063001312",
        "title": "New Custom Collection",
        "descriptionHtml": "This is a custom collection.",
        "updatedAt": "2025-06-11T20:25:18Z",
        "handle": "custom-collection",
        "image": null,
        "products": {
          "nodes": [
            {
              "id": "gid://shopify/Product/20995642",
              "featuredMedia": {
                "id": "gid://shopify/MediaImage/730211239"
              }
            }
          ]
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Create a new metafield on a new collection

  #### Description

  Create a new metafield \`my\_field.subtitle\` on a new collection. Alternatively, refer to the \[\`metafieldsSet\`]\(https://shopify.dev/docs/api/admin-graphql/latest/mutations/metafieldsset) mutation to create and update metafields on collection resources.

  #### Query

  ```graphql
  mutation createCollectionMetafields($input: CollectionInput!) {
    collectionCreate(input: $input) {
      collection {
        id
        metafields(first: 3) {
          edges {
            node {
              id
              namespace
              key
              value
            }
          }
        }
      }
      userErrors {
        message
        field
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "metafields": [
        {
          "namespace": "my_field",
          "key": "subtitle",
          "type": "single_line_text_field",
          "value": "Bold Colors"
        }
      ],
      "title": "Spring Styles"
    }
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation createCollectionMetafields($input: CollectionInput!) { collectionCreate(input: $input) { collection { id metafields(first: 3) { edges { node { id namespace key value } } } } userErrors { message field } } }",
   "variables": {
      "input": {
        "metafields": [
          {
            "namespace": "my_field",
            "key": "subtitle",
            "type": "single_line_text_field",
            "value": "Bold Colors"
          }
        ],
        "title": "Spring Styles"
      }
    }
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    mutation createCollectionMetafields($input: CollectionInput!) {
      collectionCreate(input: $input) {
        collection {
          id
          metafields(first: 3) {
            edges {
              node {
                id
                namespace
                key
                value
              }
            }
          }
        }
        userErrors {
          message
          field
        }
      }
    }`,
    {
      variables: {
          "input": {
              "metafields": [
                  {
                      "namespace": "my_field",
                      "key": "subtitle",
                      "type": "single_line_text_field",
                      "value": "Bold Colors"
                  }
              ],
              "title": "Spring Styles"
          }
      },
    },
    );
    const json = await response.json();
    return json.data;
  }
  ```

  #### Ruby

  ```ruby
  session = ShopifyAPI::Auth::Session.new(
    shop: "your-development-store.myshopify.com",
    access_token: access_token
  )
  client = ShopifyAPI::Clients::Graphql::Admin.new(
    session: session
  )

  query = <<~QUERY
    mutation createCollectionMetafields($input: CollectionInput!) {
      collectionCreate(input: $input) {
        collection {
          id
          metafields(first: 3) {
            edges {
              node {
                id
                namespace
                key
                value
              }
            }
          }
        }
        userErrors {
          message
          field
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "metafields": [
        {
          "namespace": "my_field",
          "key": "subtitle",
          "type": "single_line_text_field",
          "value": "Bold Colors"
        }
      ],
      "title": "Spring Styles"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation createCollectionMetafields($input: CollectionInput!) {
        collectionCreate(input: $input) {
          collection {
            id
            metafields(first: 3) {
              edges {
                node {
                  id
                  namespace
                  key
                  value
                }
              }
            }
          }
          userErrors {
            message
            field
          }
        }
      }`,
      "variables": {
          "input": {
              "metafields": [
                  {
                      "namespace": "my_field",
                      "key": "subtitle",
                      "type": "single_line_text_field",
                      "value": "Bold Colors"
                  }
              ],
              "title": "Spring Styles"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation createCollectionMetafields($input: CollectionInput!) {
    collectionCreate(input: $input) {
      collection {
        id
        metafields(first: 3) {
          edges {
            node {
              id
              namespace
              key
              value
            }
          }
        }
      }
      userErrors {
        message
        field
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "metafields": [
        {
          "namespace": "my_field",
          "key": "subtitle",
          "type": "single_line_text_field",
          "value": "Bold Colors"
        }
      ],
      "title": "Spring Styles"
    }
  }'
  ```

  #### Response

  ```json
  {
    "collectionCreate": {
      "collection": {
        "id": "gid://shopify/Collection/1063001315",
        "metafields": {
          "edges": [
            {
              "node": {
                "id": "gid://shopify/Metafield/1069228935",
                "namespace": "my_field",
                "key": "subtitle",
                "value": "Bold Colors"
              }
            }
          ]
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Create a smart collection

  #### Description

  Create a \[smart collection]\(https://help.shopify.com/manual/products/collections/smart-collections), specifically tailored for a store's shoe collection. The response returns the details of the newly created collection, including its ID, title, description, handle, sort order, and the defined rule set in the \[collection's conditions]\(https://help.shopify.com/manual/products/collections/smart-collections/conditions).

  #### Query

  ```graphql
  mutation CollectionCreate($input: CollectionInput!) {
    collectionCreate(input: $input) {
      userErrors {
        field
        message
      }
      collection {
        id
        title
        descriptionHtml
        handle
        sortOrder
        ruleSet {
          appliedDisjunctively
          rules {
            column
            relation
            condition
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "title": "Our entire shoe collection",
      "descriptionHtml": "View <b>every</b> shoe available in our store.",
      "ruleSet": {
        "appliedDisjunctively": false,
        "rules": {
          "column": "TITLE",
          "relation": "CONTAINS",
          "condition": "shoe"
        }
      }
    }
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation CollectionCreate($input: CollectionInput!) { collectionCreate(input: $input) { userErrors { field message } collection { id title descriptionHtml handle sortOrder ruleSet { appliedDisjunctively rules { column relation condition } } } } }",
   "variables": {
      "input": {
        "title": "Our entire shoe collection",
        "descriptionHtml": "View <b>every</b> shoe available in our store.",
        "ruleSet": {
          "appliedDisjunctively": false,
          "rules": {
            "column": "TITLE",
            "relation": "CONTAINS",
            "condition": "shoe"
          }
        }
      }
    }
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    mutation CollectionCreate($input: CollectionInput!) {
      collectionCreate(input: $input) {
        userErrors {
          field
          message
        }
        collection {
          id
          title
          descriptionHtml
          handle
          sortOrder
          ruleSet {
            appliedDisjunctively
            rules {
              column
              relation
              condition
            }
          }
        }
      }
    }`,
    {
      variables: {
          "input": {
              "title": "Our entire shoe collection",
              "descriptionHtml": "View <b>every</b> shoe available in our store.",
              "ruleSet": {
                  "appliedDisjunctively": false,
                  "rules": {
                      "column": "TITLE",
                      "relation": "CONTAINS",
                      "condition": "shoe"
                  }
              }
          }
      },
    },
    );
    const json = await response.json();
    return json.data;
  }
  ```

  #### Ruby

  ```ruby
  session = ShopifyAPI::Auth::Session.new(
    shop: "your-development-store.myshopify.com",
    access_token: access_token
  )
  client = ShopifyAPI::Clients::Graphql::Admin.new(
    session: session
  )

  query = <<~QUERY
    mutation CollectionCreate($input: CollectionInput!) {
      collectionCreate(input: $input) {
        userErrors {
          field
          message
        }
        collection {
          id
          title
          descriptionHtml
          handle
          sortOrder
          ruleSet {
            appliedDisjunctively
            rules {
              column
              relation
              condition
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "title": "Our entire shoe collection",
      "descriptionHtml": "View <b>every</b> shoe available in our store.",
      "ruleSet": {
        "appliedDisjunctively": false,
        "rules": {
          "column": "TITLE",
          "relation": "CONTAINS",
          "condition": "shoe"
        }
      }
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation CollectionCreate($input: CollectionInput!) {
        collectionCreate(input: $input) {
          userErrors {
            field
            message
          }
          collection {
            id
            title
            descriptionHtml
            handle
            sortOrder
            ruleSet {
              appliedDisjunctively
              rules {
                column
                relation
                condition
              }
            }
          }
        }
      }`,
      "variables": {
          "input": {
              "title": "Our entire shoe collection",
              "descriptionHtml": "View <b>every</b> shoe available in our store.",
              "ruleSet": {
                  "appliedDisjunctively": false,
                  "rules": {
                      "column": "TITLE",
                      "relation": "CONTAINS",
                      "condition": "shoe"
                  }
              }
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation CollectionCreate($input: CollectionInput!) {
    collectionCreate(input: $input) {
      userErrors {
        field
        message
      }
      collection {
        id
        title
        descriptionHtml
        handle
        sortOrder
        ruleSet {
          appliedDisjunctively
          rules {
            column
            relation
            condition
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "title": "Our entire shoe collection",
      "descriptionHtml": "View <b>every</b> shoe available in our store.",
      "ruleSet": {
        "appliedDisjunctively": false,
        "rules": {
          "column": "TITLE",
          "relation": "CONTAINS",
          "condition": "shoe"
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "collectionCreate": {
      "userErrors": [],
      "collection": {
        "id": "gid://shopify/Collection/1063001311",
        "title": "Our entire shoe collection",
        "descriptionHtml": "View <b>every</b> shoe available in our store.",
        "handle": "our-entire-shoe-collection",
        "sortOrder": "BEST_SELLING",
        "ruleSet": {
          "appliedDisjunctively": false,
          "rules": [
            {
              "column": "TITLE",
              "relation": "CONTAINS",
              "condition": "shoe"
            }
          ]
        }
      }
    }
  }
  ```

* ### Create a smart collection with metafield definition conditions

  #### Description

  Create a \[smart collection]\(https://help.shopify.com/manual/products/collections/smart-collections) that contains all products with the specific product and variant \[metafield definition conditions]\(https://shopify.dev/docs/apps/build/custom-data/metafields/definitions). The collection includes all products that have the product metafield value \`leather\` and the variant metafield value \`true\`.

  #### Query

  ```graphql
  mutation CollectionCreate($input: CollectionInput!) {
    collectionCreate(input: $input) {
      userErrors {
        field
        message
      }
      collection {
        id
        title
        descriptionHtml
        handle
        sortOrder
        ruleSet {
          appliedDisjunctively
          rules {
            column
            relation
            condition
            conditionObject {
              ... on CollectionRuleMetafieldCondition {
                metafieldDefinition {
                  id
                  name
                  type {
                    name
                  }
                  ownerType
                }
              }
            }
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "title": "Our entire leather collection",
      "descriptionHtml": "Check out our leather products.",
      "ruleSet": {
        "appliedDisjunctively": false,
        "rules": [
          {
            "column": "PRODUCT_METAFIELD_DEFINITION",
            "relation": "EQUALS",
            "condition": "leather",
            "conditionObjectId": "gid://shopify/MetafieldDefinition/1071456107"
          },
          {
            "column": "VARIANT_METAFIELD_DEFINITION",
            "relation": "EQUALS",
            "condition": "true",
            "conditionObjectId": "gid://shopify/MetafieldDefinition/1071456108"
          }
        ]
      }
    }
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation CollectionCreate($input: CollectionInput!) { collectionCreate(input: $input) { userErrors { field message } collection { id title descriptionHtml handle sortOrder ruleSet { appliedDisjunctively rules { column relation condition conditionObject { ... on CollectionRuleMetafieldCondition { metafieldDefinition { id name type { name } ownerType } } } } } } } }",
   "variables": {
      "input": {
        "title": "Our entire leather collection",
        "descriptionHtml": "Check out our leather products.",
        "ruleSet": {
          "appliedDisjunctively": false,
          "rules": [
            {
              "column": "PRODUCT_METAFIELD_DEFINITION",
              "relation": "EQUALS",
              "condition": "leather",
              "conditionObjectId": "gid://shopify/MetafieldDefinition/1071456107"
            },
            {
              "column": "VARIANT_METAFIELD_DEFINITION",
              "relation": "EQUALS",
              "condition": "true",
              "conditionObjectId": "gid://shopify/MetafieldDefinition/1071456108"
            }
          ]
        }
      }
    }
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    mutation CollectionCreate($input: CollectionInput!) {
      collectionCreate(input: $input) {
        userErrors {
          field
          message
        }
        collection {
          id
          title
          descriptionHtml
          handle
          sortOrder
          ruleSet {
            appliedDisjunctively
            rules {
              column
              relation
              condition
              conditionObject {
                ... on CollectionRuleMetafieldCondition {
                  metafieldDefinition {
                    id
                    name
                    type {
                      name
                    }
                    ownerType
                  }
                }
              }
            }
          }
        }
      }
    }`,
    {
      variables: {
          "input": {
              "title": "Our entire leather collection",
              "descriptionHtml": "Check out our leather products.",
              "ruleSet": {
                  "appliedDisjunctively": false,
                  "rules": [
                      {
                          "column": "PRODUCT_METAFIELD_DEFINITION",
                          "relation": "EQUALS",
                          "condition": "leather",
                          "conditionObjectId": "gid://shopify/MetafieldDefinition/1071456107"
                      },
                      {
                          "column": "VARIANT_METAFIELD_DEFINITION",
                          "relation": "EQUALS",
                          "condition": "true",
                          "conditionObjectId": "gid://shopify/MetafieldDefinition/1071456108"
                      }
                  ]
              }
          }
      },
    },
    );
    const json = await response.json();
    return json.data;
  }
  ```

  #### Ruby

  ```ruby
  session = ShopifyAPI::Auth::Session.new(
    shop: "your-development-store.myshopify.com",
    access_token: access_token
  )
  client = ShopifyAPI::Clients::Graphql::Admin.new(
    session: session
  )

  query = <<~QUERY
    mutation CollectionCreate($input: CollectionInput!) {
      collectionCreate(input: $input) {
        userErrors {
          field
          message
        }
        collection {
          id
          title
          descriptionHtml
          handle
          sortOrder
          ruleSet {
            appliedDisjunctively
            rules {
              column
              relation
              condition
              conditionObject {
                ... on CollectionRuleMetafieldCondition {
                  metafieldDefinition {
                    id
                    name
                    type {
                      name
                    }
                    ownerType
                  }
                }
              }
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "title": "Our entire leather collection",
      "descriptionHtml": "Check out our leather products.",
      "ruleSet": {
        "appliedDisjunctively": false,
        "rules": [
          {
            "column": "PRODUCT_METAFIELD_DEFINITION",
            "relation": "EQUALS",
            "condition": "leather",
            "conditionObjectId": "gid://shopify/MetafieldDefinition/1071456107"
          },
          {
            "column": "VARIANT_METAFIELD_DEFINITION",
            "relation": "EQUALS",
            "condition": "true",
            "conditionObjectId": "gid://shopify/MetafieldDefinition/1071456108"
          }
        ]
      }
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation CollectionCreate($input: CollectionInput!) {
        collectionCreate(input: $input) {
          userErrors {
            field
            message
          }
          collection {
            id
            title
            descriptionHtml
            handle
            sortOrder
            ruleSet {
              appliedDisjunctively
              rules {
                column
                relation
                condition
                conditionObject {
                  ... on CollectionRuleMetafieldCondition {
                    metafieldDefinition {
                      id
                      name
                      type {
                        name
                      }
                      ownerType
                    }
                  }
                }
              }
            }
          }
        }
      }`,
      "variables": {
          "input": {
              "title": "Our entire leather collection",
              "descriptionHtml": "Check out our leather products.",
              "ruleSet": {
                  "appliedDisjunctively": false,
                  "rules": [
                      {
                          "column": "PRODUCT_METAFIELD_DEFINITION",
                          "relation": "EQUALS",
                          "condition": "leather",
                          "conditionObjectId": "gid://shopify/MetafieldDefinition/1071456107"
                      },
                      {
                          "column": "VARIANT_METAFIELD_DEFINITION",
                          "relation": "EQUALS",
                          "condition": "true",
                          "conditionObjectId": "gid://shopify/MetafieldDefinition/1071456108"
                      }
                  ]
              }
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation CollectionCreate($input: CollectionInput!) {
    collectionCreate(input: $input) {
      userErrors {
        field
        message
      }
      collection {
        id
        title
        descriptionHtml
        handle
        sortOrder
        ruleSet {
          appliedDisjunctively
          rules {
            column
            relation
            condition
            conditionObject {
              ... on CollectionRuleMetafieldCondition {
                metafieldDefinition {
                  id
                  name
                  type {
                    name
                  }
                  ownerType
                }
              }
            }
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "title": "Our entire leather collection",
      "descriptionHtml": "Check out our leather products.",
      "ruleSet": {
        "appliedDisjunctively": false,
        "rules": [
          {
            "column": "PRODUCT_METAFIELD_DEFINITION",
            "relation": "EQUALS",
            "condition": "leather",
            "conditionObjectId": "gid://shopify/MetafieldDefinition/1071456107"
          },
          {
            "column": "VARIANT_METAFIELD_DEFINITION",
            "relation": "EQUALS",
            "condition": "true",
            "conditionObjectId": "gid://shopify/MetafieldDefinition/1071456108"
          }
        ]
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "collectionCreate": {
      "userErrors": [],
      "collection": {
        "id": "gid://shopify/Collection/1063001314",
        "title": "Our entire leather collection",
        "descriptionHtml": "Check out our leather products.",
        "handle": "our-entire-leather-collection",
        "sortOrder": "BEST_SELLING",
        "ruleSet": {
          "appliedDisjunctively": false,
          "rules": [
            {
              "column": "PRODUCT_METAFIELD_DEFINITION",
              "relation": "EQUALS",
              "condition": "leather",
              "conditionObject": {
                "metafieldDefinition": {
                  "id": "gid://shopify/MetafieldDefinition/1071456107",
                  "name": "Material",
                  "type": {
                    "name": "single_line_text_field"
                  },
                  "ownerType": "PRODUCT"
                }
              }
            },
            {
              "column": "VARIANT_METAFIELD_DEFINITION",
              "relation": "EQUALS",
              "condition": "true",
              "conditionObject": {
                "metafieldDefinition": {
                  "id": "gid://shopify/MetafieldDefinition/1071456108",
                  "name": "Imported",
                  "type": {
                    "name": "boolean"
                  },
                  "ownerType": "PRODUCTVARIANT"
                }
              }
            }
          ]
        }
      }
    }
  }
  ```

* ### collectionCreate reference
