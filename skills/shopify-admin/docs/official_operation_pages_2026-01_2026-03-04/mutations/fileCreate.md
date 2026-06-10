---
title: fileCreate - GraphQL Admin
description: >-
  Creates file assets for a store from external URLs or files that were
  previously uploaded using the

  [`stagedUploadsCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/stageduploadscreate)

  mutation.


  Use the `fileCreate` mutation to add various types of media and documents to
  your store. These files are added to the

  [**Files** page](https://shopify.com/admin/settings/files) in the Shopify
  admin and can be referenced by other

  resources in your store.


  The `fileCreate` mutation supports multiple file types:


  - **Images**: Product photos, variant images, and general store imagery

  - **Videos**: Shopify-hosted videos for product demonstrations and marketing

  - **External videos**: YouTube and Vimeo videos for enhanced product
  experiences

  - **3D models**: Interactive 3D representations of products

  - **Generic files**: PDFs, documents, and other file types for store resources


  The mutation handles duplicate filenames using configurable resolution modes
  that automatically append UUIDs,

  replace existing files, or raise errors when conflicts occur.


  > Note:

  > Files are processed asynchronously. Check the

  >
  [`fileStatus`](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/File#fields-fileStatus)

  > field to monitor processing completion. The maximum number of files that can
  be created in a single batch is 250.


  After creating files, you can make subsequent updates using the following
  mutations:


  -
  [`fileUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/fileUpdate):

  Update file properties such as alt text or replace file contents while
  preserving the same URL.

  -
  [`fileDelete`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/fileDelete):

  Remove files from your store when they are no longer needed.


  To list all files in your store, use the

  [`files`](https://shopify.dev/docs/api/admin-graphql/latest/queries/files)
  query.


  Learn how to manage

  [product media and file
  assets](https://shopify.dev/docs/apps/build/online-store/product-media)

  in your app.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/fileCreate'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/fileCreate.md'
---

# file​Create

mutation

Requires `write_files` access scope, `write_themes` access scope or `write_images` access scope. Also: Users must have create files permissions.

Creates file assets for a store from external URLs or files that were previously uploaded using the [`stagedUploadsCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/stageduploadscreate) mutation.

Use the `fileCreate` mutation to add various types of media and documents to your store. These files are added to the [**Files** page](https://shopify.com/admin/settings/files) in the Shopify admin and can be referenced by other resources in your store.

The `fileCreate` mutation supports multiple file types:

* **Images**: Product photos, variant images, and general store imagery
* **Videos**: Shopify-hosted videos for product demonstrations and marketing
* **External videos**: YouTube and Vimeo videos for enhanced product experiences
* **3D models**: Interactive 3D representations of products
* **Generic files**: PDFs, documents, and other file types for store resources

The mutation handles duplicate filenames using configurable resolution modes that automatically append UUIDs, replace existing files, or raise errors when conflicts occur.

***

**Note:** Files are processed asynchronously. Check the \<a href="https://shopify.dev/docs/api/admin-graphql/latest/interfaces/File#fields-fileStatus">\<code>\<span class="PreventFireFoxApplyingGapToWBR">file\<wbr/>Status\</span>\</code>\</a> field to monitor processing completion. The maximum number of files that can be created in a single batch is 250.

***

After creating files, you can make subsequent updates using the following mutations:

* [`fileUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/fileUpdate): Update file properties such as alt text or replace file contents while preserving the same URL.
* [`fileDelete`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/fileDelete): Remove files from your store when they are no longer needed.

To list all files in your store, use the [`files`](https://shopify.dev/docs/api/admin-graphql/latest/queries/files) query.

Learn how to manage [product media and file assets](https://shopify.dev/docs/apps/build/online-store/product-media) in your app.

## Arguments

* files

  [\[File​Create​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/FileCreateInput)

  required

  List of new files to be created.

***

## File​Create​Payload returns

* files

  [\[File!\]](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/File)

  The newly created files.

* user​Errors

  [\[Files​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/FilesUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a file using a staged upload URL

  #### Description

  Create a file asset using a staged upload URL after uploading the file using the \[\`stagedUploadsCreate\`]\(https://shopify.dev/docs/api/admin-graphql/latest/mutations/stagedUploadsCreate) mutation. This two-step process allows you to first upload large files to a temporary staging location, then create the file record. The example demonstrates creating an image file from a staged upload, which is ideal for large files or batch uploads. The response returns the file ID, upload status, alt text, creation timestamp, and image dimensions. Learn more about \[managing media for products]\(https://shopify.dev/docs/apps/build/online-store/product-media) and \[uploading files]\(https://help.shopify.com/manual/shopify-admin/productivity-tools/file-uploads).

  #### Query

  ```graphql
  mutation fileCreate($files: [FileCreateInput!]!) {
    fileCreate(files: $files) {
      files {
        id
        fileStatus
        alt
        createdAt
        ... on MediaImage {
          image {
            width
            height
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
    "files": [
      {
        "alt": "Product showcase image from staged upload",
        "contentType": "IMAGE",
        "originalSource": "https://snowdevil.myshopify.com/admin/tmp/files/staged-image-upload-123.jpg"
      }
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
  "query": "mutation fileCreate($files: [FileCreateInput!]!) { fileCreate(files: $files) { files { id fileStatus alt createdAt ... on MediaImage { image { width height } } } userErrors { field message } } }",
   "variables": {
      "files": [
        {
          "alt": "Product showcase image from staged upload",
          "contentType": "IMAGE",
          "originalSource": "https://snowdevil.myshopify.com/admin/tmp/files/staged-image-upload-123.jpg"
        }
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
    mutation fileCreate($files: [FileCreateInput!]!) {
      fileCreate(files: $files) {
        files {
          id
          fileStatus
          alt
          createdAt
          ... on MediaImage {
            image {
              width
              height
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
          "files": [
              {
                  "alt": "Product showcase image from staged upload",
                  "contentType": "IMAGE",
                  "originalSource": "https://snowdevil.myshopify.com/admin/tmp/files/staged-image-upload-123.jpg"
              }
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
    mutation fileCreate($files: [FileCreateInput!]!) {
      fileCreate(files: $files) {
        files {
          id
          fileStatus
          alt
          createdAt
          ... on MediaImage {
            image {
              width
              height
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
    "files": [
      {
        "alt": "Product showcase image from staged upload",
        "contentType": "IMAGE",
        "originalSource": "https://snowdevil.myshopify.com/admin/tmp/files/staged-image-upload-123.jpg"
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation fileCreate($files: [FileCreateInput!]!) {
        fileCreate(files: $files) {
          files {
            id
            fileStatus
            alt
            createdAt
            ... on MediaImage {
              image {
                width
                height
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
          "files": [
              {
                  "alt": "Product showcase image from staged upload",
                  "contentType": "IMAGE",
                  "originalSource": "https://snowdevil.myshopify.com/admin/tmp/files/staged-image-upload-123.jpg"
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation fileCreate($files: [FileCreateInput!]!) {
    fileCreate(files: $files) {
      files {
        id
        fileStatus
        alt
        createdAt
        ... on MediaImage {
          image {
            width
            height
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
    "files": [
      {
        "alt": "Product showcase image from staged upload",
        "contentType": "IMAGE",
        "originalSource": "https://snowdevil.myshopify.com/admin/tmp/files/staged-image-upload-123.jpg"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "fileCreate": {
      "files": [
        {
          "id": "gid://shopify/MediaImage/1072273436",
          "fileStatus": "READY",
          "alt": "Product showcase image from staged upload",
          "createdAt": "2025-06-21T03:47:03Z",
          "image": {
            "width": 372,
            "height": 110
          }
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### Create mixed media files with custom filenames

  #### Description

  Create different types of media files including images and documents with custom filenames for better organization. This example demonstrates how to handle multiple \[\`contentType\`]\(https://shopify.dev/docs/api/admin-graphql/latest/enums/FileContentType) values in a single file creation operation with descriptive naming conventions. The mutation downloads content from external URLs and creates file records simultaneously, each with appropriate metadata and custom filenames that reflect their purpose. The response returns file IDs, upload status, alt text, and creation timestamps, plus type-specific data like image dimensions and document URLs.

  #### Query

  ```graphql
  mutation fileCreate($files: [FileCreateInput!]!) {
    fileCreate(files: $files) {
      files {
        id
        fileStatus
        alt
        createdAt
        ... on MediaImage {
          image {
            width
            height
          }
        }
        ... on GenericFile {
          url
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
    "files": [
      {
        "alt": "High-resolution product showcase image",
        "contentType": "IMAGE",
        "originalSource": "https://burst.shopifycdn.com/photos/product-photo.jpg",
        "filename": "product-hero-image.jpg"
      },
      {
        "alt": "Technical specifications and dimensions",
        "contentType": "FILE",
        "originalSource": "https://example.com/specifications.pdf",
        "filename": "technical-specifications.pdf"
      },
      {
        "alt": "Product inventory and pricing data",
        "contentType": "FILE",
        "originalSource": "https://example.com/product-data.xlsx",
        "filename": "product-data-sheet.xlsx"
      }
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
  "query": "mutation fileCreate($files: [FileCreateInput!]!) { fileCreate(files: $files) { files { id fileStatus alt createdAt ... on MediaImage { image { width height } } ... on GenericFile { url } } userErrors { field message } } }",
   "variables": {
      "files": [
        {
          "alt": "High-resolution product showcase image",
          "contentType": "IMAGE",
          "originalSource": "https://burst.shopifycdn.com/photos/product-photo.jpg",
          "filename": "product-hero-image.jpg"
        },
        {
          "alt": "Technical specifications and dimensions",
          "contentType": "FILE",
          "originalSource": "https://example.com/specifications.pdf",
          "filename": "technical-specifications.pdf"
        },
        {
          "alt": "Product inventory and pricing data",
          "contentType": "FILE",
          "originalSource": "https://example.com/product-data.xlsx",
          "filename": "product-data-sheet.xlsx"
        }
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
    mutation fileCreate($files: [FileCreateInput!]!) {
      fileCreate(files: $files) {
        files {
          id
          fileStatus
          alt
          createdAt
          ... on MediaImage {
            image {
              width
              height
            }
          }
          ... on GenericFile {
            url
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
          "files": [
              {
                  "alt": "High-resolution product showcase image",
                  "contentType": "IMAGE",
                  "originalSource": "https://burst.shopifycdn.com/photos/product-photo.jpg",
                  "filename": "product-hero-image.jpg"
              },
              {
                  "alt": "Technical specifications and dimensions",
                  "contentType": "FILE",
                  "originalSource": "https://example.com/specifications.pdf",
                  "filename": "technical-specifications.pdf"
              },
              {
                  "alt": "Product inventory and pricing data",
                  "contentType": "FILE",
                  "originalSource": "https://example.com/product-data.xlsx",
                  "filename": "product-data-sheet.xlsx"
              }
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
    mutation fileCreate($files: [FileCreateInput!]!) {
      fileCreate(files: $files) {
        files {
          id
          fileStatus
          alt
          createdAt
          ... on MediaImage {
            image {
              width
              height
            }
          }
          ... on GenericFile {
            url
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
    "files": [
      {
        "alt": "High-resolution product showcase image",
        "contentType": "IMAGE",
        "originalSource": "https://burst.shopifycdn.com/photos/product-photo.jpg",
        "filename": "product-hero-image.jpg"
      },
      {
        "alt": "Technical specifications and dimensions",
        "contentType": "FILE",
        "originalSource": "https://example.com/specifications.pdf",
        "filename": "technical-specifications.pdf"
      },
      {
        "alt": "Product inventory and pricing data",
        "contentType": "FILE",
        "originalSource": "https://example.com/product-data.xlsx",
        "filename": "product-data-sheet.xlsx"
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation fileCreate($files: [FileCreateInput!]!) {
        fileCreate(files: $files) {
          files {
            id
            fileStatus
            alt
            createdAt
            ... on MediaImage {
              image {
                width
                height
              }
            }
            ... on GenericFile {
              url
            }
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "files": [
              {
                  "alt": "High-resolution product showcase image",
                  "contentType": "IMAGE",
                  "originalSource": "https://burst.shopifycdn.com/photos/product-photo.jpg",
                  "filename": "product-hero-image.jpg"
              },
              {
                  "alt": "Technical specifications and dimensions",
                  "contentType": "FILE",
                  "originalSource": "https://example.com/specifications.pdf",
                  "filename": "technical-specifications.pdf"
              },
              {
                  "alt": "Product inventory and pricing data",
                  "contentType": "FILE",
                  "originalSource": "https://example.com/product-data.xlsx",
                  "filename": "product-data-sheet.xlsx"
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation fileCreate($files: [FileCreateInput!]!) {
    fileCreate(files: $files) {
      files {
        id
        fileStatus
        alt
        createdAt
        ... on MediaImage {
          image {
            width
            height
          }
        }
        ... on GenericFile {
          url
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
    "files": [
      {
        "alt": "High-resolution product showcase image",
        "contentType": "IMAGE",
        "originalSource": "https://burst.shopifycdn.com/photos/product-photo.jpg",
        "filename": "product-hero-image.jpg"
      },
      {
        "alt": "Technical specifications and dimensions",
        "contentType": "FILE",
        "originalSource": "https://example.com/specifications.pdf",
        "filename": "technical-specifications.pdf"
      },
      {
        "alt": "Product inventory and pricing data",
        "contentType": "FILE",
        "originalSource": "https://example.com/product-data.xlsx",
        "filename": "product-data-sheet.xlsx"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "fileCreate": {
      "files": [
        {
          "id": "gid://shopify/MediaImage/1072273439",
          "fileStatus": "READY",
          "alt": "High-resolution product showcase image",
          "createdAt": "2025-06-21T03:47:11Z",
          "image": {
            "width": 372,
            "height": 110
          }
        },
        {
          "id": "gid://shopify/GenericFile/1072273440",
          "fileStatus": "READY",
          "alt": "Technical specifications and dimensions",
          "createdAt": "2025-06-21T03:47:11Z",
          "url": "https://cdn.shopify.com/s/files/1/2637/1970/files/specifications.pdf?v=1750477634"
        },
        {
          "id": "gid://shopify/GenericFile/1072273441",
          "fileStatus": "READY",
          "alt": "Product inventory and pricing data",
          "createdAt": "2025-06-21T03:47:12Z",
          "url": "https://cdn.shopify.com/s/files/1/2637/1970/files/product-data.xlsx?v=1750477637"
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### Create product documentation files from external URLs

  #### Description

  Create product documentation files such as user manuals, warranty information, and installation guides. This example shows how to create PDF and text files from external URLs that customers can download for product support. The response returns file IDs, upload status, alt text, creation timestamps, and download URLs for each created document. Learn more about \[managing media for products]\(https://shopify.dev/docs/apps/build/online-store/product-media) and \[uploading files]\(https://help.shopify.com/manual/shopify-admin/productivity-tools/file-uploads).

  #### Query

  ```graphql
  mutation fileCreate($files: [FileCreateInput!]!) {
    fileCreate(files: $files) {
      files {
        id
        fileStatus
        alt
        createdAt
        ... on GenericFile {
          url
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
    "files": [
      {
        "alt": "Complete user manual and setup instructions",
        "contentType": "FILE",
        "originalSource": "https://example.com/user-manual.pdf",
        "filename": "product-user-manual.pdf"
      },
      {
        "alt": "Warranty terms and conditions document",
        "contentType": "FILE",
        "originalSource": "https://example.com/warranty-info.txt",
        "filename": "warranty-information.txt"
      }
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
  "query": "mutation fileCreate($files: [FileCreateInput!]!) { fileCreate(files: $files) { files { id fileStatus alt createdAt ... on GenericFile { url } } userErrors { field message } } }",
   "variables": {
      "files": [
        {
          "alt": "Complete user manual and setup instructions",
          "contentType": "FILE",
          "originalSource": "https://example.com/user-manual.pdf",
          "filename": "product-user-manual.pdf"
        },
        {
          "alt": "Warranty terms and conditions document",
          "contentType": "FILE",
          "originalSource": "https://example.com/warranty-info.txt",
          "filename": "warranty-information.txt"
        }
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
    mutation fileCreate($files: [FileCreateInput!]!) {
      fileCreate(files: $files) {
        files {
          id
          fileStatus
          alt
          createdAt
          ... on GenericFile {
            url
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
          "files": [
              {
                  "alt": "Complete user manual and setup instructions",
                  "contentType": "FILE",
                  "originalSource": "https://example.com/user-manual.pdf",
                  "filename": "product-user-manual.pdf"
              },
              {
                  "alt": "Warranty terms and conditions document",
                  "contentType": "FILE",
                  "originalSource": "https://example.com/warranty-info.txt",
                  "filename": "warranty-information.txt"
              }
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
    mutation fileCreate($files: [FileCreateInput!]!) {
      fileCreate(files: $files) {
        files {
          id
          fileStatus
          alt
          createdAt
          ... on GenericFile {
            url
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
    "files": [
      {
        "alt": "Complete user manual and setup instructions",
        "contentType": "FILE",
        "originalSource": "https://example.com/user-manual.pdf",
        "filename": "product-user-manual.pdf"
      },
      {
        "alt": "Warranty terms and conditions document",
        "contentType": "FILE",
        "originalSource": "https://example.com/warranty-info.txt",
        "filename": "warranty-information.txt"
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation fileCreate($files: [FileCreateInput!]!) {
        fileCreate(files: $files) {
          files {
            id
            fileStatus
            alt
            createdAt
            ... on GenericFile {
              url
            }
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "files": [
              {
                  "alt": "Complete user manual and setup instructions",
                  "contentType": "FILE",
                  "originalSource": "https://example.com/user-manual.pdf",
                  "filename": "product-user-manual.pdf"
              },
              {
                  "alt": "Warranty terms and conditions document",
                  "contentType": "FILE",
                  "originalSource": "https://example.com/warranty-info.txt",
                  "filename": "warranty-information.txt"
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation fileCreate($files: [FileCreateInput!]!) {
    fileCreate(files: $files) {
      files {
        id
        fileStatus
        alt
        createdAt
        ... on GenericFile {
          url
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
    "files": [
      {
        "alt": "Complete user manual and setup instructions",
        "contentType": "FILE",
        "originalSource": "https://example.com/user-manual.pdf",
        "filename": "product-user-manual.pdf"
      },
      {
        "alt": "Warranty terms and conditions document",
        "contentType": "FILE",
        "originalSource": "https://example.com/warranty-info.txt",
        "filename": "warranty-information.txt"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "fileCreate": {
      "files": [
        {
          "id": "gid://shopify/GenericFile/1072273437",
          "fileStatus": "READY",
          "alt": "Complete user manual and setup instructions",
          "createdAt": "2025-06-21T03:47:06Z",
          "url": "https://cdn.shopify.com/s/files/1/2637/1970/files/user-manual.pdf?v=1750477627"
        },
        {
          "id": "gid://shopify/GenericFile/1072273438",
          "fileStatus": "READY",
          "alt": "Warranty terms and conditions document",
          "createdAt": "2025-06-21T03:47:06Z",
          "url": "https://cdn.shopify.com/s/files/1/2637/1970/files/warranty-info.txt?v=1750477629"
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### Create product image files from external URLs

  #### Description

  Create multiple product image files from external URLs to build a visual gallery for a product. This example demonstrates creating two product image files with descriptive alt text for accessibility. The mutation downloads the images from external URLs and creates file records, returning their file IDs, upload status, alt text, creation timestamps, and image dimensions (width and height). Learn more about \[managing media for products]\(https://shopify.dev/docs/apps/build/online-store/product-media) and \[uploading files]\(https://help.shopify.com/manual/shopify-admin/productivity-tools/file-uploads).

  #### Query

  ```graphql
  mutation fileCreate($files: [FileCreateInput!]!) {
    fileCreate(files: $files) {
      files {
        id
        fileStatus
        alt
        createdAt
        ... on MediaImage {
          image {
            width
            height
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
    "files": [
      {
        "alt": "Laptop computer on modern desk setup",
        "contentType": "IMAGE",
        "originalSource": "https://burst.shopifycdn.com/photos/laptop-on-desk.jpg"
      },
      {
        "alt": "Close-up view of laptop keyboard and screen",
        "contentType": "IMAGE",
        "originalSource": "https://burst.shopifycdn.com/photos/laptop-closeup.jpg"
      }
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
  "query": "mutation fileCreate($files: [FileCreateInput!]!) { fileCreate(files: $files) { files { id fileStatus alt createdAt ... on MediaImage { image { width height } } } userErrors { field message } } }",
   "variables": {
      "files": [
        {
          "alt": "Laptop computer on modern desk setup",
          "contentType": "IMAGE",
          "originalSource": "https://burst.shopifycdn.com/photos/laptop-on-desk.jpg"
        },
        {
          "alt": "Close-up view of laptop keyboard and screen",
          "contentType": "IMAGE",
          "originalSource": "https://burst.shopifycdn.com/photos/laptop-closeup.jpg"
        }
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
    mutation fileCreate($files: [FileCreateInput!]!) {
      fileCreate(files: $files) {
        files {
          id
          fileStatus
          alt
          createdAt
          ... on MediaImage {
            image {
              width
              height
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
          "files": [
              {
                  "alt": "Laptop computer on modern desk setup",
                  "contentType": "IMAGE",
                  "originalSource": "https://burst.shopifycdn.com/photos/laptop-on-desk.jpg"
              },
              {
                  "alt": "Close-up view of laptop keyboard and screen",
                  "contentType": "IMAGE",
                  "originalSource": "https://burst.shopifycdn.com/photos/laptop-closeup.jpg"
              }
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
    mutation fileCreate($files: [FileCreateInput!]!) {
      fileCreate(files: $files) {
        files {
          id
          fileStatus
          alt
          createdAt
          ... on MediaImage {
            image {
              width
              height
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
    "files": [
      {
        "alt": "Laptop computer on modern desk setup",
        "contentType": "IMAGE",
        "originalSource": "https://burst.shopifycdn.com/photos/laptop-on-desk.jpg"
      },
      {
        "alt": "Close-up view of laptop keyboard and screen",
        "contentType": "IMAGE",
        "originalSource": "https://burst.shopifycdn.com/photos/laptop-closeup.jpg"
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation fileCreate($files: [FileCreateInput!]!) {
        fileCreate(files: $files) {
          files {
            id
            fileStatus
            alt
            createdAt
            ... on MediaImage {
              image {
                width
                height
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
          "files": [
              {
                  "alt": "Laptop computer on modern desk setup",
                  "contentType": "IMAGE",
                  "originalSource": "https://burst.shopifycdn.com/photos/laptop-on-desk.jpg"
              },
              {
                  "alt": "Close-up view of laptop keyboard and screen",
                  "contentType": "IMAGE",
                  "originalSource": "https://burst.shopifycdn.com/photos/laptop-closeup.jpg"
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation fileCreate($files: [FileCreateInput!]!) {
    fileCreate(files: $files) {
      files {
        id
        fileStatus
        alt
        createdAt
        ... on MediaImage {
          image {
            width
            height
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
    "files": [
      {
        "alt": "Laptop computer on modern desk setup",
        "contentType": "IMAGE",
        "originalSource": "https://burst.shopifycdn.com/photos/laptop-on-desk.jpg"
      },
      {
        "alt": "Close-up view of laptop keyboard and screen",
        "contentType": "IMAGE",
        "originalSource": "https://burst.shopifycdn.com/photos/laptop-closeup.jpg"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "fileCreate": {
      "files": [
        {
          "id": "gid://shopify/MediaImage/1072273434",
          "fileStatus": "READY",
          "alt": "Laptop computer on modern desk setup",
          "createdAt": "2025-06-21T03:46:57Z",
          "image": {
            "width": 372,
            "height": 110
          }
        },
        {
          "id": "gid://shopify/MediaImage/1072273435",
          "fileStatus": "READY",
          "alt": "Close-up view of laptop keyboard and screen",
          "createdAt": "2025-06-21T03:46:57Z",
          "image": {
            "width": 372,
            "height": 110
          }
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### Handle file creation errors and validation

  #### Description

  This example shows how the mutation responds to common errors like invalid URLs and unsupported file extensions. The response includes detailed user errors with specific field paths and error codes to help identify and resolve issues.

  #### Query

  ```graphql
  mutation fileCreate($files: [FileCreateInput!]!) {
    fileCreate(files: $files) {
      files {
        id
        fileStatus
        alt
        createdAt
      }
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
    "files": [
      {
        "alt": "Invalid URL example",
        "contentType": "IMAGE",
        "originalSource": "not-a-valid-url"
      },
      {
        "alt": "Unsupported file type example",
        "contentType": "IMAGE",
        "originalSource": "https://example.com/document.html"
      },
      {
        "contentType": "IMAGE",
        "originalSource": "https://example.com/image.jpg",
        "alt": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
      }
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
  "query": "mutation fileCreate($files: [FileCreateInput!]!) { fileCreate(files: $files) { files { id fileStatus alt createdAt } userErrors { field message code } } }",
   "variables": {
      "files": [
        {
          "alt": "Invalid URL example",
          "contentType": "IMAGE",
          "originalSource": "not-a-valid-url"
        },
        {
          "alt": "Unsupported file type example",
          "contentType": "IMAGE",
          "originalSource": "https://example.com/document.html"
        },
        {
          "contentType": "IMAGE",
          "originalSource": "https://example.com/image.jpg",
          "alt": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        }
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
    mutation fileCreate($files: [FileCreateInput!]!) {
      fileCreate(files: $files) {
        files {
          id
          fileStatus
          alt
          createdAt
        }
        userErrors {
          field
          message
          code
        }
      }
    }`,
    {
      variables: {
          "files": [
              {
                  "alt": "Invalid URL example",
                  "contentType": "IMAGE",
                  "originalSource": "not-a-valid-url"
              },
              {
                  "alt": "Unsupported file type example",
                  "contentType": "IMAGE",
                  "originalSource": "https://example.com/document.html"
              },
              {
                  "contentType": "IMAGE",
                  "originalSource": "https://example.com/image.jpg",
                  "alt": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
              }
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
    mutation fileCreate($files: [FileCreateInput!]!) {
      fileCreate(files: $files) {
        files {
          id
          fileStatus
          alt
          createdAt
        }
        userErrors {
          field
          message
          code
        }
      }
    }
  QUERY

  variables = {
    "files": [
      {
        "alt": "Invalid URL example",
        "contentType": "IMAGE",
        "originalSource": "not-a-valid-url"
      },
      {
        "alt": "Unsupported file type example",
        "contentType": "IMAGE",
        "originalSource": "https://example.com/document.html"
      },
      {
        "contentType": "IMAGE",
        "originalSource": "https://example.com/image.jpg",
        "alt": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation fileCreate($files: [FileCreateInput!]!) {
        fileCreate(files: $files) {
          files {
            id
            fileStatus
            alt
            createdAt
          }
          userErrors {
            field
            message
            code
          }
        }
      }`,
      "variables": {
          "files": [
              {
                  "alt": "Invalid URL example",
                  "contentType": "IMAGE",
                  "originalSource": "not-a-valid-url"
              },
              {
                  "alt": "Unsupported file type example",
                  "contentType": "IMAGE",
                  "originalSource": "https://example.com/document.html"
              },
              {
                  "contentType": "IMAGE",
                  "originalSource": "https://example.com/image.jpg",
                  "alt": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation fileCreate($files: [FileCreateInput!]!) {
    fileCreate(files: $files) {
      files {
        id
        fileStatus
        alt
        createdAt
      }
      userErrors {
        field
        message
        code
      }
    }
  }' \
  --variables \
  '{
    "files": [
      {
        "alt": "Invalid URL example",
        "contentType": "IMAGE",
        "originalSource": "not-a-valid-url"
      },
      {
        "alt": "Unsupported file type example",
        "contentType": "IMAGE",
        "originalSource": "https://example.com/document.html"
      },
      {
        "contentType": "IMAGE",
        "originalSource": "https://example.com/image.jpg",
        "alt": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "fileCreate": {
      "files": [],
      "userErrors": [
        {
          "field": [
            "files",
            "0",
            "originalSource"
          ],
          "message": "Image URL is invalid",
          "code": "INVALID"
        },
        {
          "field": [
            "files",
            "1",
            "originalSource"
          ],
          "message": "The file type is not supported.",
          "code": "UNACCEPTABLE_ASSET"
        },
        {
          "field": [
            "files",
            "2",
            "alt"
          ],
          "message": "The alt value exceeds the maximum limit of 512 characters.",
          "code": "ALT_VALUE_LIMIT_EXCEEDED"
        }
      ]
    }
  }
  ```

* ### fileCreate reference
