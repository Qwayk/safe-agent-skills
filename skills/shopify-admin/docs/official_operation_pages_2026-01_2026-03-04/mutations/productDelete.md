---
title: productDelete - GraphQL Admin
description: >-
  Permanently deletes a product and all its associated data, including variants,
  media, publications, and inventory items.


  Use the `productDelete` mutation to programmatically remove products from your
  store when they need to be

  permanently deleted from your catalog, such as when removing discontinued
  items, cleaning up test data, or

  synchronizing with external inventory management systems.


  The `productDelete` mutation removes the product from all associated
  collections,

  and removes all associated data for the product, including:


  - All product variants and their inventory items

  - Product media (images, videos) that are not referenced by other products

  - [Product
  options](https://shopify.dev/api/admin-graphql/latest/objects/ProductOption)
  and [option
  values](https://shopify.dev/api/admin-graphql/latest/objects/ProductOptionValue)

  - Product publications across all sales channels

  - Product tags and metadata associations


  The `productDelete` mutation also has the following effects on existing orders
  and transactions:


  - **Draft orders**: Existing draft orders that reference this product will
  retain the product information as stored data, but the product reference will
  be removed. Draft orders can still be completed with the stored product
  details.

  - **Completed orders and refunds**: Previously completed orders that included
  this product aren't affected. The product information in completed orders is
  preserved for record-keeping, and existing refunds for this product remain
  valid and processable.


  > Caution:

  > Product deletion is irreversible. After a product is deleted, it can't be
  recovered. Consider archiving

  > or unpublishing products instead if you might need to restore them later.


  If you need to delete a large product, such as one that has many

  [variants](https://shopify.dev/api/admin-graphql/latest/objects/ProductVariant)

  that are active at several

  [locations](https://shopify.dev/api/admin-graphql/latest/objects/Location),

  you might encounter timeout errors. To avoid these timeout errors, you can set
  the

  [`synchronous`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productDelete#arguments-synchronous)

  parameter to `false` to run the deletion asynchronously, which returns a

  [`ProductDeleteOperation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductDeleteOperation)

  that you can monitor for completion status.


  If you need more granular control over product cleanup, consider using these
  alternative mutations:


  -
  [`productUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productUpdate):

  Update the product status to archived or unpublished instead of deleting.

  -
  [`productVariantsBulkDelete`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkDelete):

  Delete specific variants while keeping the product.

  -
  [`productOptionsDelete`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsDelete):

  Delete the choices available for a product, such as size, color, or material.


  Learn more about the [product
  model](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/productDelete'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/productDelete.md'
---

# product​Delete

mutation

Requires `write_products` access scope. Also: The user must have a permission to delete products.

Permanently deletes a product and all its associated data, including variants, media, publications, and inventory items.

Use the `productDelete` mutation to programmatically remove products from your store when they need to be permanently deleted from your catalog, such as when removing discontinued items, cleaning up test data, or synchronizing with external inventory management systems.

The `productDelete` mutation removes the product from all associated collections, and removes all associated data for the product, including:

* All product variants and their inventory items
* Product media (images, videos) that are not referenced by other products
* [Product options](https://shopify.dev/api/admin-graphql/latest/objects/ProductOption) and [option values](https://shopify.dev/api/admin-graphql/latest/objects/ProductOptionValue)
* Product publications across all sales channels
* Product tags and metadata associations

The `productDelete` mutation also has the following effects on existing orders and transactions:

* **Draft orders**: Existing draft orders that reference this product will retain the product information as stored data, but the product reference will be removed. Draft orders can still be completed with the stored product details.
* **Completed orders and refunds**: Previously completed orders that included this product aren't affected. The product information in completed orders is preserved for record-keeping, and existing refunds for this product remain valid and processable.

***

**Caution:** Product deletion is irreversible. After a product is deleted, it can\&#39;t be recovered. Consider archiving or unpublishing products instead if you might need to restore them later.

***

If you need to delete a large product, such as one that has many [variants](https://shopify.dev/api/admin-graphql/latest/objects/ProductVariant) that are active at several [locations](https://shopify.dev/api/admin-graphql/latest/objects/Location), you might encounter timeout errors. To avoid these timeout errors, you can set the [`synchronous`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productDelete#arguments-synchronous) parameter to `false` to run the deletion asynchronously, which returns a [`ProductDeleteOperation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductDeleteOperation) that you can monitor for completion status.

If you need more granular control over product cleanup, consider using these alternative mutations:

* [`productUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productUpdate): Update the product status to archived or unpublished instead of deleting.
* [`productVariantsBulkDelete`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkDelete): Delete specific variants while keeping the product.
* [`productOptionsDelete`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsDelete): Delete the choices available for a product, such as size, color, or material.

Learn more about the [product model](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model).

## Arguments

* input

  [Product​Delete​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ProductDeleteInput)

  required

  Specifies the product to delete by its ID.

* synchronous

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:true

  Specifies whether or not to run the mutation synchronously.

***

## Product​Delete​Payload returns

* deleted​Product​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the deleted product.

* product​Delete​Operation

  [Product​Delete​Operation](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductDeleteOperation)

  The product delete operation, returned when run in asynchronous mode.

* shop

  [Shop!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Shop)

  non-null

  The shop associated with the product.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Delete a non-existent product

  #### Description

  Trying to delete a non-existent product returns \`null\`.

  #### Query

  ```graphql
  mutation {
    productDelete(input: {id: "gid://shopify/Product/-1"}) {
      deletedProductId
      userErrors {
        field
        message
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
  "query": "mutation { productDelete(input: {id: \"gid://shopify/Product/-1\"}) { deletedProductId userErrors { field message } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    mutation {
      productDelete(input: {id: "gid://shopify/Product/-1"}) {
        deletedProductId
        userErrors {
          field
          message
        }
      }
    }`,
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
    mutation {
      productDelete(input: {id: "gid://shopify/Product/-1"}) {
        deletedProductId
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `mutation {
      productDelete(input: {id: "gid://shopify/Product/-1"}) {
        deletedProductId
        userErrors {
          field
          message
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation {
    productDelete(input: {id: "gid://shopify/Product/-1"}) {
      deletedProductId
      userErrors {
        field
        message
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "productDelete": {
      "deletedProductId": null,
      "userErrors": [
        {
          "field": [
            "id"
          ],
          "message": "Product does not exist"
        }
      ]
    }
  }
  ```

* ### Delete a product

  #### Query

  ```graphql
  mutation {
    productDelete(input: {id: "gid://shopify/Product/108828309"}) {
      deletedProductId
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
  "query": "mutation { productDelete(input: {id: \"gid://shopify/Product/108828309\"}) { deletedProductId } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    mutation {
      productDelete(input: {id: "gid://shopify/Product/108828309"}) {
        deletedProductId
      }
    }`,
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
    mutation {
      productDelete(input: {id: "gid://shopify/Product/108828309"}) {
        deletedProductId
      }
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `mutation {
      productDelete(input: {id: "gid://shopify/Product/108828309"}) {
        deletedProductId
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation {
    productDelete(input: {id: "gid://shopify/Product/108828309"}) {
      deletedProductId
    }
  }'
  ```

  #### Response

  ```json
  {
    "productDelete": {
      "deletedProductId": "gid://shopify/Product/108828309"
    }
  }
  ```

* ### Delete a product asynchronously and return a product delete operation

  #### Query

  ```graphql
  mutation productDelete($input: ProductDeleteInput!, $synchronous: Boolean!) {
    productDelete(synchronous: $synchronous, input: $input) {
      deletedProductId
      productDeleteOperation {
        id
        status
        deletedProductId
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "synchronous": false,
    "input": {
      "id": "gid://shopify/Product/108828309"
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
  "query": "mutation productDelete($input: ProductDeleteInput!, $synchronous: Boolean!) { productDelete(synchronous: $synchronous, input: $input) { deletedProductId productDeleteOperation { id status deletedProductId } } }",
   "variables": {
      "synchronous": false,
      "input": {
        "id": "gid://shopify/Product/108828309"
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
    mutation productDelete($input: ProductDeleteInput!, $synchronous: Boolean!) {
      productDelete(synchronous: $synchronous, input: $input) {
        deletedProductId
        productDeleteOperation {
          id
          status
          deletedProductId
        }
      }
    }`,
    {
      variables: {
          "synchronous": false,
          "input": {
              "id": "gid://shopify/Product/108828309"
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
    mutation productDelete($input: ProductDeleteInput!, $synchronous: Boolean!) {
      productDelete(synchronous: $synchronous, input: $input) {
        deletedProductId
        productDeleteOperation {
          id
          status
          deletedProductId
        }
      }
    }
  QUERY

  variables = {
    "synchronous": false,
    "input": {
      "id": "gid://shopify/Product/108828309"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation productDelete($input: ProductDeleteInput!, $synchronous: Boolean!) {
        productDelete(synchronous: $synchronous, input: $input) {
          deletedProductId
          productDeleteOperation {
            id
            status
            deletedProductId
          }
        }
      }`,
      "variables": {
          "synchronous": false,
          "input": {
              "id": "gid://shopify/Product/108828309"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation productDelete($input: ProductDeleteInput!, $synchronous: Boolean!) {
    productDelete(synchronous: $synchronous, input: $input) {
      deletedProductId
      productDeleteOperation {
        id
        status
        deletedProductId
      }
    }
  }' \
  --variables \
  '{
    "synchronous": false,
    "input": {
      "id": "gid://shopify/Product/108828309"
    }
  }'
  ```

  #### Response

  ```json
  {
    "productDelete": {
      "deletedProductId": null,
      "productDeleteOperation": {
        "id": "gid://shopify/ProductDeleteOperation/1010603706",
        "status": "CREATED",
        "deletedProductId": null
      }
    }
  }
  ```

* ### productDelete reference
