---
title: fileDelete - GraphQL Admin
description: >-
  Deletes file assets that were previously uploaded to your store.


  Use the `fileDelete` mutation to permanently remove media and file assets from
  your store when they are no longer needed.

  This mutation handles the complete removal of files from both your store's
  file library and any associated references

  to products or other resources.


  The `fileDelete` mutation supports removal of multiple file types:


  - **Images**: Product photos, variant images, and general store imagery

  - **Videos**: Shopify-hosted videos for product demonstrations and marketing
  content

  - **External Videos**: YouTube and Vimeo videos linked to your products

  - **3D models**: Interactive 3D representations of products

  - **Generic files**: PDFs, documents, and other file types stored in your

  [**Files** page](https://shopify.com/admin/settings/files)


  When you delete files that are referenced by products, the mutation
  automatically removes those references and

  reorders any remaining media to maintain proper positioning. Product file
  references are database relationships

  managed through a media reference system, not just links in product
  descriptions. The Shopify admin provides a UI

  to manage these relationships, and when files are deleted, the system
  automatically cleans up all references.

  Files that are currently being processed by other operations are rejected to
  prevent conflicts.


  > Caution:

  > File deletion is permanent and can't be undone. When you delete a file
  that's being used in your store,

  > it will immediately stop appearing wherever it was displayed. For example,
  if you delete a product image,

  > that product will show a broken image or placeholder on your storefront and
  in the admin. The same applies

  > to any other files linked from themes, blog posts, or pages. Before deleting
  files, you can use the

  > [`files` query](https://shopify.dev/api/admin-graphql/latest/queries/files)
  to list and review

  > your store's file assets.


  Learn how to manage

  [product media and file
  assets](https://shopify.dev/docs/apps/build/online-store/product-media)

  in your app.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/fileDelete'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/fileDelete.md'
---

# file​Delete

mutation

Requires `write_files` access scope. Also: Users must have delete files permissions.

Deletes file assets that were previously uploaded to your store.

Use the `fileDelete` mutation to permanently remove media and file assets from your store when they are no longer needed. This mutation handles the complete removal of files from both your store's file library and any associated references to products or other resources.

The `fileDelete` mutation supports removal of multiple file types:

* **Images**: Product photos, variant images, and general store imagery
* **Videos**: Shopify-hosted videos for product demonstrations and marketing content
* **External Videos**: YouTube and Vimeo videos linked to your products
* **3D models**: Interactive 3D representations of products
* **Generic files**: PDFs, documents, and other file types stored in your [**Files** page](https://shopify.com/admin/settings/files)

When you delete files that are referenced by products, the mutation automatically removes those references and reorders any remaining media to maintain proper positioning. Product file references are database relationships managed through a media reference system, not just links in product descriptions. The Shopify admin provides a UI to manage these relationships, and when files are deleted, the system automatically cleans up all references. Files that are currently being processed by other operations are rejected to prevent conflicts.

***

**Caution:** File deletion is permanent and can\&#39;t be undone. When you delete a file that\&#39;s being used in your store, it will immediately stop appearing wherever it was displayed. For example, if you delete a product image, that product will show a broken image or placeholder on your storefront and in the admin. The same applies to any other files linked from themes, blog posts, or pages. Before deleting files, you can use the \<a href="https://shopify.dev/api/admin-graphql/latest/queries/files">\<code>files\</code> query\</a> to list and review your store\&#39;s file assets.

***

Learn how to manage [product media and file assets](https://shopify.dev/docs/apps/build/online-store/product-media) in your app.

## Arguments

* file​Ids

  [\[ID!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The IDs of the files to be deleted.

***

## File​Delete​Payload returns

* deleted​File​Ids

  [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The IDs of the deleted files.

* user​Errors

  [\[Files​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/FilesUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Delete multiple file types

  #### Description

  Delete multiple types of files from your store's media library to clean up unused assets and free up storage space. This example demonstrates batch deletion of images and documents in a single operation for efficient media library management. Batch deletion is useful for removing outdated assets, cleaning up after product updates, or organizing your file storage. The response returns the IDs of successfully deleted files, confirming which assets have been permanently removed from your store.

  #### Query

  ```graphql
  mutation fileDelete($fileIds: [ID!]!) {
    fileDelete(fileIds: $fileIds) {
      deletedFileIds
      userErrors {
        field
        message
        code
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "fileIds": [
      "gid://shopify/GenericFile/1072273762",
      "gid://shopify/MediaImage/1072273763",
      "gid://shopify/MediaImage/1072273764",
      "gid://shopify/GenericFile/1072273765"
    ]
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation fileDelete($fileIds: [ID!]!) { fileDelete(fileIds: $fileIds) { deletedFileIds userErrors { field message code } } }",
   "variables": {
      "fileIds": [
        "gid://shopify/GenericFile/1072273762",
        "gid://shopify/MediaImage/1072273763",
        "gid://shopify/MediaImage/1072273764",
        "gid://shopify/GenericFile/1072273765"
      ]
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
    mutation fileDelete($fileIds: [ID!]!) {
      fileDelete(fileIds: $fileIds) {
        deletedFileIds
        userErrors {
          field
          message
          code
        }
      }
    }`,
    {
      variables: {
          "fileIds": [
              "gid://shopify/GenericFile/1072273762",
              "gid://shopify/MediaImage/1072273763",
              "gid://shopify/MediaImage/1072273764",
              "gid://shopify/GenericFile/1072273765"
          ]
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
    mutation fileDelete($fileIds: [ID!]!) {
      fileDelete(fileIds: $fileIds) {
        deletedFileIds
        userErrors {
          field
          message
          code
        }
      }
    }
  QUERY

  variables = {
    "fileIds": [
      "gid://shopify/GenericFile/1072273762",
      "gid://shopify/MediaImage/1072273763",
      "gid://shopify/MediaImage/1072273764",
      "gid://shopify/GenericFile/1072273765"
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation fileDelete($fileIds: [ID!]!) {
        fileDelete(fileIds: $fileIds) {
          deletedFileIds
          userErrors {
            field
            message
            code
          }
        }
      }`,
      "variables": {
          "fileIds": [
              "gid://shopify/GenericFile/1072273762",
              "gid://shopify/MediaImage/1072273763",
              "gid://shopify/MediaImage/1072273764",
              "gid://shopify/GenericFile/1072273765"
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation fileDelete($fileIds: [ID!]!) {
    fileDelete(fileIds: $fileIds) {
      deletedFileIds
      userErrors {
        field
        message
        code
      }
    }
  }' \
  --variables \
  '{
    "fileIds": [
      "gid://shopify/GenericFile/1072273762",
      "gid://shopify/MediaImage/1072273763",
      "gid://shopify/MediaImage/1072273764",
      "gid://shopify/GenericFile/1072273765"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "fileDelete": {
      "deletedFileIds": [
        "gid://shopify/GenericFile/1072273762",
        "gid://shopify/MediaImage/1072273763",
        "gid://shopify/MediaImage/1072273764",
        "gid://shopify/GenericFile/1072273765"
      ],
      "userErrors": []
    }
  }
  ```

* ### Delete product-associated files and clean up references

  #### Description

  Delete product-associated files and clean up all product references and media positioning. This example deletes two product images from a gallery and demonstrates how Shopify automatically reorders remaining media to maintain proper sequencing.

  #### Query

  ```graphql
  mutation fileDelete($fileIds: [ID!]!) {
    fileDelete(fileIds: $fileIds) {
      deletedFileIds
      userErrors {
        field
        message
        code
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "fileIds": [
      "gid://shopify/MediaImage/1072273759",
      "gid://shopify/MediaImage/1072273761"
    ]
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation fileDelete($fileIds: [ID!]!) { fileDelete(fileIds: $fileIds) { deletedFileIds userErrors { field message code } } }",
   "variables": {
      "fileIds": [
        "gid://shopify/MediaImage/1072273759",
        "gid://shopify/MediaImage/1072273761"
      ]
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
    mutation fileDelete($fileIds: [ID!]!) {
      fileDelete(fileIds: $fileIds) {
        deletedFileIds
        userErrors {
          field
          message
          code
        }
      }
    }`,
    {
      variables: {
          "fileIds": [
              "gid://shopify/MediaImage/1072273759",
              "gid://shopify/MediaImage/1072273761"
          ]
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
    mutation fileDelete($fileIds: [ID!]!) {
      fileDelete(fileIds: $fileIds) {
        deletedFileIds
        userErrors {
          field
          message
          code
        }
      }
    }
  QUERY

  variables = {
    "fileIds": [
      "gid://shopify/MediaImage/1072273759",
      "gid://shopify/MediaImage/1072273761"
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation fileDelete($fileIds: [ID!]!) {
        fileDelete(fileIds: $fileIds) {
          deletedFileIds
          userErrors {
            field
            message
            code
          }
        }
      }`,
      "variables": {
          "fileIds": [
              "gid://shopify/MediaImage/1072273759",
              "gid://shopify/MediaImage/1072273761"
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation fileDelete($fileIds: [ID!]!) {
    fileDelete(fileIds: $fileIds) {
      deletedFileIds
      userErrors {
        field
        message
        code
      }
    }
  }' \
  --variables \
  '{
    "fileIds": [
      "gid://shopify/MediaImage/1072273759",
      "gid://shopify/MediaImage/1072273761"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "fileDelete": {
      "deletedFileIds": [
        "gid://shopify/MediaImage/1072273759",
        "gid://shopify/MediaImage/1072273761"
      ],
      "userErrors": []
    }
  }
  ```

* ### Handle file deletion errors and validation

  #### Description

  This example demonstrates how the fileDelete mutation handles various error conditions when files cannot be deleted. Common errors include attempting to delete files that don't exist, files that are currently locked by other operations, or invalid file IDs. The response provides detailed \[error information]\(https://shopify.dev/docs/api/admin-graphql/latest/mutations/fileDelete#returns-userErrors) with specific file IDs and error codes to help identify which files couldn't be deleted and why. Proper error handling ensures reliable file management workflows and helps prevent data loss or unexpected behavior.

  #### Query

  ```graphql
  mutation fileDelete($fileIds: [ID!]!) {
    fileDelete(fileIds: $fileIds) {
      deletedFileIds
      userErrors {
        field
        message
        code
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "fileIds": [
      "gid://shopify/GenericFile/999999",
      "gid://shopify/GenericFile/1072273766",
      "gid://shopify/MediaImage/1072273767"
    ]
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation fileDelete($fileIds: [ID!]!) { fileDelete(fileIds: $fileIds) { deletedFileIds userErrors { field message code } } }",
   "variables": {
      "fileIds": [
        "gid://shopify/GenericFile/999999",
        "gid://shopify/GenericFile/1072273766",
        "gid://shopify/MediaImage/1072273767"
      ]
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
    mutation fileDelete($fileIds: [ID!]!) {
      fileDelete(fileIds: $fileIds) {
        deletedFileIds
        userErrors {
          field
          message
          code
        }
      }
    }`,
    {
      variables: {
          "fileIds": [
              "gid://shopify/GenericFile/999999",
              "gid://shopify/GenericFile/1072273766",
              "gid://shopify/MediaImage/1072273767"
          ]
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
    mutation fileDelete($fileIds: [ID!]!) {
      fileDelete(fileIds: $fileIds) {
        deletedFileIds
        userErrors {
          field
          message
          code
        }
      }
    }
  QUERY

  variables = {
    "fileIds": [
      "gid://shopify/GenericFile/999999",
      "gid://shopify/GenericFile/1072273766",
      "gid://shopify/MediaImage/1072273767"
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation fileDelete($fileIds: [ID!]!) {
        fileDelete(fileIds: $fileIds) {
          deletedFileIds
          userErrors {
            field
            message
            code
          }
        }
      }`,
      "variables": {
          "fileIds": [
              "gid://shopify/GenericFile/999999",
              "gid://shopify/GenericFile/1072273766",
              "gid://shopify/MediaImage/1072273767"
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation fileDelete($fileIds: [ID!]!) {
    fileDelete(fileIds: $fileIds) {
      deletedFileIds
      userErrors {
        field
        message
        code
      }
    }
  }' \
  --variables \
  '{
    "fileIds": [
      "gid://shopify/GenericFile/999999",
      "gid://shopify/GenericFile/1072273766",
      "gid://shopify/MediaImage/1072273767"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "fileDelete": {
      "deletedFileIds": null,
      "userErrors": [
        {
          "field": [
            "fileIds"
          ],
          "message": "File id gid://shopify/GenericFile/999999 does not exist.",
          "code": "FILE_DOES_NOT_EXIST"
        }
      ]
    }
  }
  ```

* ### fileDelete reference
