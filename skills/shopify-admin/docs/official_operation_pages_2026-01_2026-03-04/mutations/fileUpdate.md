---
title: fileUpdate - GraphQL Admin
description: >-
  Updates properties, content, and metadata associated with an existing file
  asset that has already been uploaded to Shopify.


  Use the `fileUpdate` mutation to modify various aspects of files already
  stored in your store.

  Files can be updated individually or in batches.


  The `fileUpdate` mutation supports updating multiple file properties:


  - **Alt text**: Update accessibility descriptions for images and other media.

  - **File content**: Replace image or generic file content while maintaining
  the same URL.

  - **Filename**: Modify file names (extension must match the original).

  - **Product references**: Add or remove associations between files and
  products. Removing file-product associations

  deletes the file from the product's media gallery and clears the image from
  any product variants that were using it.


  The mutation handles different file types with specific capabilities:


  - **Images**: Update preview images, original source, filename, and alt text.

  - **Generic files**: Update original source, filename, and alt text.

  - **Videos and 3D models**: Update alt text and product references.


  > Note:

  > Files must be in `ready` state before they can be updated. The mutation
  includes file locking to prevent

  > conflicts during updates. You can't simultaneously update both
  `originalSource` and `previewImageSource`.


  After updating files, you can use related mutations for additional file
  management:


  -
  [`fileCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/fileCreate):

  Create new file assets from external URLs or staged uploads.

  -
  [`fileDelete`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/fileDelete):

  Remove files from your store when they are no longer needed.


  Learn how to manage

  [product media and file
  assets](https://shopify.dev/docs/apps/build/online-store/product-media)

  in your app.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/fileUpdate'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/fileUpdate.md'
---

# file​Update

mutation

Requires `write_files` access scope or `write_themes` access scope. Also: Users must have edit files permissions.

Updates properties, content, and metadata associated with an existing file asset that has already been uploaded to Shopify.

Use the `fileUpdate` mutation to modify various aspects of files already stored in your store. Files can be updated individually or in batches.

The `fileUpdate` mutation supports updating multiple file properties:

* **Alt text**: Update accessibility descriptions for images and other media.
* **File content**: Replace image or generic file content while maintaining the same URL.
* **Filename**: Modify file names (extension must match the original).
* **Product references**: Add or remove associations between files and products. Removing file-product associations deletes the file from the product's media gallery and clears the image from any product variants that were using it.

The mutation handles different file types with specific capabilities:

* **Images**: Update preview images, original source, filename, and alt text.
* **Generic files**: Update original source, filename, and alt text.
* **Videos and 3D models**: Update alt text and product references.

***

**Note:** Files must be in \<code>ready\</code> state before they can be updated. The mutation includes file locking to prevent conflicts during updates. You can\&#39;t simultaneously update both \<code>\<span class="PreventFireFoxApplyingGapToWBR">original\<wbr/>Source\</span>\</code> and \<code>\<span class="PreventFireFoxApplyingGapToWBR">preview\<wbr/>Image\<wbr/>Source\</span>\</code>.

***

After updating files, you can use related mutations for additional file management:

* [`fileCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/fileCreate): Create new file assets from external URLs or staged uploads.
* [`fileDelete`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/fileDelete): Remove files from your store when they are no longer needed.

Learn how to manage [product media and file assets](https://shopify.dev/docs/apps/build/online-store/product-media) in your app.

## Arguments

* files

  [\[File​Update​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/FileUpdateInput)

  required

  List of files to be updated.

***

## File​Update​Payload returns

* files

  [\[File!\]](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/File)

  The list of updated files.

* user​Errors

  [\[Files​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/FilesUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Handle file update errors and validation

  #### Description

  This example demonstrates how the \`fileUpdate\` mutation handles various error conditions and validation failures. Common errors include files that don't exist, alt text that exceeds length limits, and invalid source URLs. The response provides detailed error information with specific field paths and error codes using the \[\`userErrors\`]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError) object to help you identify and resolve issues quickly.

  #### Query

  ```graphql
  mutation fileUpdate($files: [FileUpdateInput!]!) {
    fileUpdate(files: $files) {
      files {
        id
        alt
        fileStatus
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
        "id": "gid://shopify/GenericFile/999999",
        "alt": "File that doesn't exist"
      },
      {
        "id": "gid://shopify/GenericFile/1072273825",
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
  "query": "mutation fileUpdate($files: [FileUpdateInput!]!) { fileUpdate(files: $files) { files { id alt fileStatus } userErrors { field message code } } }",
   "variables": {
      "files": [
        {
          "id": "gid://shopify/GenericFile/999999",
          "alt": "File that doesn'\''t exist"
        },
        {
          "id": "gid://shopify/GenericFile/1072273825",
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
    mutation fileUpdate($files: [FileUpdateInput!]!) {
      fileUpdate(files: $files) {
        files {
          id
          alt
          fileStatus
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
                  "id": "gid://shopify/GenericFile/999999",
                  "alt": "File that doesn't exist"
              },
              {
                  "id": "gid://shopify/GenericFile/1072273825",
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
    mutation fileUpdate($files: [FileUpdateInput!]!) {
      fileUpdate(files: $files) {
        files {
          id
          alt
          fileStatus
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
        "id": "gid://shopify/GenericFile/999999",
        "alt": "File that doesn't exist"
      },
      {
        "id": "gid://shopify/GenericFile/1072273825",
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
      "query": `mutation fileUpdate($files: [FileUpdateInput!]!) {
        fileUpdate(files: $files) {
          files {
            id
            alt
            fileStatus
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
                  "id": "gid://shopify/GenericFile/999999",
                  "alt": "File that doesn't exist"
              },
              {
                  "id": "gid://shopify/GenericFile/1072273825",
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
  'mutation fileUpdate($files: [FileUpdateInput!]!) {
    fileUpdate(files: $files) {
      files {
        id
        alt
        fileStatus
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
        "id": "gid://shopify/GenericFile/999999",
        "alt": "File that doesn't exist"
      },
      {
        "id": "gid://shopify/GenericFile/1072273825",
        "alt": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "fileUpdate": {
      "files": [],
      "userErrors": [
        {
          "field": [
            "files"
          ],
          "message": "File id [\"gid://shopify/GenericFile/999999\"] does not exist.",
          "code": "FILE_DOES_NOT_EXIST"
        }
      ]
    }
  }
  ```

* ### Update a file's alt text and other metadata

  #### Description

  Update a file's alt text and other metadata to improve accessibility. This example demonstrates updating the alt text of an existing \[image file]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/MediaImage) to provide better context for screen readers and search engines. The response returns the updated file with its new alt text, file status, and creation timestamp.

  #### Query

  ```graphql
  mutation fileUpdate($files: [FileUpdateInput!]!) {
    fileUpdate(files: $files) {
      files {
        id
        alt
        fileStatus
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
        "id": "gid://shopify/MediaImage/1072273831",
        "alt": "High-resolution product image showing laptop computer on modern desk with wireless accessories"
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
  "query": "mutation fileUpdate($files: [FileUpdateInput!]!) { fileUpdate(files: $files) { files { id alt fileStatus createdAt ... on MediaImage { image { width height } } } userErrors { field message code } } }",
   "variables": {
      "files": [
        {
          "id": "gid://shopify/MediaImage/1072273831",
          "alt": "High-resolution product image showing laptop computer on modern desk with wireless accessories"
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
    mutation fileUpdate($files: [FileUpdateInput!]!) {
      fileUpdate(files: $files) {
        files {
          id
          alt
          fileStatus
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
          code
        }
      }
    }`,
    {
      variables: {
          "files": [
              {
                  "id": "gid://shopify/MediaImage/1072273831",
                  "alt": "High-resolution product image showing laptop computer on modern desk with wireless accessories"
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
    mutation fileUpdate($files: [FileUpdateInput!]!) {
      fileUpdate(files: $files) {
        files {
          id
          alt
          fileStatus
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
          code
        }
      }
    }
  QUERY

  variables = {
    "files": [
      {
        "id": "gid://shopify/MediaImage/1072273831",
        "alt": "High-resolution product image showing laptop computer on modern desk with wireless accessories"
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
      "query": `mutation fileUpdate($files: [FileUpdateInput!]!) {
        fileUpdate(files: $files) {
          files {
            id
            alt
            fileStatus
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
            code
          }
        }
      }`,
      "variables": {
          "files": [
              {
                  "id": "gid://shopify/MediaImage/1072273831",
                  "alt": "High-resolution product image showing laptop computer on modern desk with wireless accessories"
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
  'mutation fileUpdate($files: [FileUpdateInput!]!) {
    fileUpdate(files: $files) {
      files {
        id
        alt
        fileStatus
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
        code
      }
    }
  }' \
  --variables \
  '{
    "files": [
      {
        "id": "gid://shopify/MediaImage/1072273831",
        "alt": "High-resolution product image showing laptop computer on modern desk with wireless accessories"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "fileUpdate": {
      "files": [
        {
          "id": "gid://shopify/MediaImage/1072273831",
          "alt": "High-resolution product image showing laptop computer on modern desk with wireless accessories",
          "fileStatus": "READY",
          "createdAt": "2025-06-22T09:19:04Z",
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

* ### Update file content by replacing the source URL

  #### Description

  Update the actual content of a file by providing a new source URL while maintaining the same file ID and URL structure. This example shows how to replace an image file's content with a new version from a different URL, useful for updating product photos or correcting image issues. The operation preserves the file's existing metadata and associations while updating the underlying image data. The response includes the \[\`fileStatus\`]\(https://shopify.dev/docs/api/admin-graphql/latest/enums/FileStatus) which will show as \`READY\` initially and may change to \`PROCESSING\` during the background update job. Learn more about \[managing media for products]\(https://shopify.dev/docs/apps/build/online-store/product-media) and \[uploading files]\(https://help.shopify.com/manual/shopify-admin/productivity-tools/file-uploads).

  #### Query

  ```graphql
  mutation fileUpdate($files: [FileUpdateInput!]!) {
    fileUpdate(files: $files) {
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
        "id": "gid://shopify/MediaImage/1072273829",
        "originalSource": "https://burst.shopifycdn.com/photos/updated-product-photo.jpg"
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
  "query": "mutation fileUpdate($files: [FileUpdateInput!]!) { fileUpdate(files: $files) { files { id fileStatus alt createdAt } userErrors { field message code } } }",
   "variables": {
      "files": [
        {
          "id": "gid://shopify/MediaImage/1072273829",
          "originalSource": "https://burst.shopifycdn.com/photos/updated-product-photo.jpg"
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
    mutation fileUpdate($files: [FileUpdateInput!]!) {
      fileUpdate(files: $files) {
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
                  "id": "gid://shopify/MediaImage/1072273829",
                  "originalSource": "https://burst.shopifycdn.com/photos/updated-product-photo.jpg"
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
    mutation fileUpdate($files: [FileUpdateInput!]!) {
      fileUpdate(files: $files) {
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
        "id": "gid://shopify/MediaImage/1072273829",
        "originalSource": "https://burst.shopifycdn.com/photos/updated-product-photo.jpg"
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
      "query": `mutation fileUpdate($files: [FileUpdateInput!]!) {
        fileUpdate(files: $files) {
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
                  "id": "gid://shopify/MediaImage/1072273829",
                  "originalSource": "https://burst.shopifycdn.com/photos/updated-product-photo.jpg"
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
  'mutation fileUpdate($files: [FileUpdateInput!]!) {
    fileUpdate(files: $files) {
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
        "id": "gid://shopify/MediaImage/1072273829",
        "originalSource": "https://burst.shopifycdn.com/photos/updated-product-photo.jpg"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "fileUpdate": {
      "files": [
        {
          "id": "gid://shopify/MediaImage/1072273829",
          "fileStatus": "READY",
          "alt": "derp",
          "createdAt": "2025-06-22T09:19:03Z"
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### Update multiple files with different operations

  #### Description

  Perform multiple update operations on different files in a single request. This example demonstrates updating alt text on multiple files simultaneously to improve accessibility across your media library. Batch operations allow you to make multiple changes efficiently and maintain consistent metadata across related files. The response includes individual file updates showing the new alt text and the \[\`fileStatus\`]\(https://shopify.dev/docs/api/admin-graphql/latest/enums/FileStatus) for each updated file. Learn more about \[managing media for products]\(https://shopify.dev/docs/apps/build/online-store/product-media) and \[web accessibility]\(https://help.shopify.com/manual/online-store/images/alt-text).

  #### Query

  ```graphql
  mutation fileUpdate($files: [FileUpdateInput!]!) {
    fileUpdate(files: $files) {
      files {
        id
        alt
        fileStatus
        ... on MediaImage {
          image {
            width
            height
          }
        }
        ... on Video {
          sources {
            url
            width
            height
          }
        }
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
        "id": "gid://shopify/MediaImage/1072273826",
        "alt": "Professional product photography showcasing laptop in modern office environment"
      },
      {
        "id": "gid://shopify/Video/1072273827",
        "alt": "Product demonstration video showing laptop features and capabilities"
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
  "query": "mutation fileUpdate($files: [FileUpdateInput!]!) { fileUpdate(files: $files) { files { id alt fileStatus ... on MediaImage { image { width height } } ... on Video { sources { url width height } } } userErrors { field message code } } }",
   "variables": {
      "files": [
        {
          "id": "gid://shopify/MediaImage/1072273826",
          "alt": "Professional product photography showcasing laptop in modern office environment"
        },
        {
          "id": "gid://shopify/Video/1072273827",
          "alt": "Product demonstration video showing laptop features and capabilities"
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
    mutation fileUpdate($files: [FileUpdateInput!]!) {
      fileUpdate(files: $files) {
        files {
          id
          alt
          fileStatus
          ... on MediaImage {
            image {
              width
              height
            }
          }
          ... on Video {
            sources {
              url
              width
              height
            }
          }
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
                  "id": "gid://shopify/MediaImage/1072273826",
                  "alt": "Professional product photography showcasing laptop in modern office environment"
              },
              {
                  "id": "gid://shopify/Video/1072273827",
                  "alt": "Product demonstration video showing laptop features and capabilities"
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
    mutation fileUpdate($files: [FileUpdateInput!]!) {
      fileUpdate(files: $files) {
        files {
          id
          alt
          fileStatus
          ... on MediaImage {
            image {
              width
              height
            }
          }
          ... on Video {
            sources {
              url
              width
              height
            }
          }
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
        "id": "gid://shopify/MediaImage/1072273826",
        "alt": "Professional product photography showcasing laptop in modern office environment"
      },
      {
        "id": "gid://shopify/Video/1072273827",
        "alt": "Product demonstration video showing laptop features and capabilities"
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
      "query": `mutation fileUpdate($files: [FileUpdateInput!]!) {
        fileUpdate(files: $files) {
          files {
            id
            alt
            fileStatus
            ... on MediaImage {
              image {
                width
                height
              }
            }
            ... on Video {
              sources {
                url
                width
                height
              }
            }
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
                  "id": "gid://shopify/MediaImage/1072273826",
                  "alt": "Professional product photography showcasing laptop in modern office environment"
              },
              {
                  "id": "gid://shopify/Video/1072273827",
                  "alt": "Product demonstration video showing laptop features and capabilities"
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
  'mutation fileUpdate($files: [FileUpdateInput!]!) {
    fileUpdate(files: $files) {
      files {
        id
        alt
        fileStatus
        ... on MediaImage {
          image {
            width
            height
          }
        }
        ... on Video {
          sources {
            url
            width
            height
          }
        }
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
        "id": "gid://shopify/MediaImage/1072273826",
        "alt": "Professional product photography showcasing laptop in modern office environment"
      },
      {
        "id": "gid://shopify/Video/1072273827",
        "alt": "Product demonstration video showing laptop features and capabilities"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "fileUpdate": {
      "files": [
        {
          "id": "gid://shopify/MediaImage/1072273826",
          "alt": "Professional product photography showcasing laptop in modern office environment",
          "fileStatus": "READY",
          "image": {
            "width": 372,
            "height": 110
          }
        },
        {
          "id": "gid://shopify/Video/1072273827",
          "alt": "Product demonstration video showing laptop features and capabilities",
          "fileStatus": "READY",
          "sources": [
            {
              "url": "https://cdn.shopify.com/videos/:/vp/some_hash/some_other_hash.m3u8",
              "width": 1280,
              "height": 720
            },
            {
              "url": "https://cdn.shopify.com/videos/c/vp/some_hash/some_other_hash.HD-720p-4.5Mbps.mp4",
              "width": 1280,
              "height": 720
            },
            {
              "url": "https://cdn.shopify.com/videos/c/vp/some_hash/some_other_hash.SD-480p-1.5Mbps.mp4",
              "width": 854,
              "height": 480
            }
          ]
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### Update the preview image for a video file

  #### Description

  Update the preview image (thumbnail) for a video file to provide a better visual representation in your store. This example shows how to change the preview image of an existing video by providing a new image URL. Shopify will download, validate, process, and optimize your image from the provided URL before using it as the thumbnail. The response includes the updated file information and the \[\`fileStatus\`]\(https://shopify.dev/docs/api/admin-graphql/latest/enums/FileStatus) for the new preview image. Learn more about \[managing media for products]\(https://shopify.dev/docs/apps/build/online-store/product-media) and \[uploading files]\(https://help.shopify.com/manual/shopify-admin/productivity-tools/file-uploads).

  #### Query

  ```graphql
  mutation fileUpdate($files: [FileUpdateInput!]!) {
    fileUpdate(files: $files) {
      files {
        id
        alt
        fileStatus
        ... on Video {
          sources {
            url
            width
            height
          }
        }
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
        "id": "gid://shopify/Video/1072273828",
        "previewImageSource": "https://burst.shopifycdn.com/photos/video-thumbnail.jpg"
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
  "query": "mutation fileUpdate($files: [FileUpdateInput!]!) { fileUpdate(files: $files) { files { id alt fileStatus ... on Video { sources { url width height } } } userErrors { field message code } } }",
   "variables": {
      "files": [
        {
          "id": "gid://shopify/Video/1072273828",
          "previewImageSource": "https://burst.shopifycdn.com/photos/video-thumbnail.jpg"
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
    mutation fileUpdate($files: [FileUpdateInput!]!) {
      fileUpdate(files: $files) {
        files {
          id
          alt
          fileStatus
          ... on Video {
            sources {
              url
              width
              height
            }
          }
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
                  "id": "gid://shopify/Video/1072273828",
                  "previewImageSource": "https://burst.shopifycdn.com/photos/video-thumbnail.jpg"
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
    mutation fileUpdate($files: [FileUpdateInput!]!) {
      fileUpdate(files: $files) {
        files {
          id
          alt
          fileStatus
          ... on Video {
            sources {
              url
              width
              height
            }
          }
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
        "id": "gid://shopify/Video/1072273828",
        "previewImageSource": "https://burst.shopifycdn.com/photos/video-thumbnail.jpg"
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
      "query": `mutation fileUpdate($files: [FileUpdateInput!]!) {
        fileUpdate(files: $files) {
          files {
            id
            alt
            fileStatus
            ... on Video {
              sources {
                url
                width
                height
              }
            }
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
                  "id": "gid://shopify/Video/1072273828",
                  "previewImageSource": "https://burst.shopifycdn.com/photos/video-thumbnail.jpg"
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
  'mutation fileUpdate($files: [FileUpdateInput!]!) {
    fileUpdate(files: $files) {
      files {
        id
        alt
        fileStatus
        ... on Video {
          sources {
            url
            width
            height
          }
        }
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
        "id": "gid://shopify/Video/1072273828",
        "previewImageSource": "https://burst.shopifycdn.com/photos/video-thumbnail.jpg"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "fileUpdate": {
      "files": [
        {
          "id": "gid://shopify/Video/1072273828",
          "alt": "",
          "fileStatus": "READY",
          "sources": [
            {
              "url": "https://cdn.shopify.com/videos/:/vp/some_hash/some_other_hash.m3u8",
              "width": 1280,
              "height": 720
            },
            {
              "url": "https://cdn.shopify.com/videos/c/vp/some_hash/some_other_hash.HD-720p-4.5Mbps.mp4",
              "width": 1280,
              "height": 720
            },
            {
              "url": "https://cdn.shopify.com/videos/c/vp/some_hash/some_other_hash.SD-480p-1.5Mbps.mp4",
              "width": 854,
              "height": 480
            }
          ]
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### Update video file metadata

  #### Description

  Update a video file's metadata such as alt text to improve accessibility and provide better context for users. This example demonstrates updating the alt text of a video file to describe its content for screen readers and search engines. The response returns the updated \[video]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Video) with its new metadata, \[file status]\(https://shopify.dev/docs/api/admin-graphql/latest/enums/FileStatus), and video source information. Learn more about \[managing media for products]\(https://shopify.dev/docs/apps/build/online-store/product-media) and \[web accessibility]\(https://help.shopify.com/manual/online-store/images/alt-text).

  #### Query

  ```graphql
  mutation fileUpdate($files: [FileUpdateInput!]!) {
    fileUpdate(files: $files) {
      files {
        id
        fileStatus
        alt
        createdAt
        ... on Video {
          sources {
            url
            width
            height
          }
        }
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
        "id": "gid://shopify/Video/1072273830",
        "alt": "Product demonstration video showing step-by-step assembly instructions and safety guidelines"
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
  "query": "mutation fileUpdate($files: [FileUpdateInput!]!) { fileUpdate(files: $files) { files { id fileStatus alt createdAt ... on Video { sources { url width height } } } userErrors { field message code } } }",
   "variables": {
      "files": [
        {
          "id": "gid://shopify/Video/1072273830",
          "alt": "Product demonstration video showing step-by-step assembly instructions and safety guidelines"
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
    mutation fileUpdate($files: [FileUpdateInput!]!) {
      fileUpdate(files: $files) {
        files {
          id
          fileStatus
          alt
          createdAt
          ... on Video {
            sources {
              url
              width
              height
            }
          }
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
                  "id": "gid://shopify/Video/1072273830",
                  "alt": "Product demonstration video showing step-by-step assembly instructions and safety guidelines"
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
    mutation fileUpdate($files: [FileUpdateInput!]!) {
      fileUpdate(files: $files) {
        files {
          id
          fileStatus
          alt
          createdAt
          ... on Video {
            sources {
              url
              width
              height
            }
          }
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
        "id": "gid://shopify/Video/1072273830",
        "alt": "Product demonstration video showing step-by-step assembly instructions and safety guidelines"
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
      "query": `mutation fileUpdate($files: [FileUpdateInput!]!) {
        fileUpdate(files: $files) {
          files {
            id
            fileStatus
            alt
            createdAt
            ... on Video {
              sources {
                url
                width
                height
              }
            }
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
                  "id": "gid://shopify/Video/1072273830",
                  "alt": "Product demonstration video showing step-by-step assembly instructions and safety guidelines"
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
  'mutation fileUpdate($files: [FileUpdateInput!]!) {
    fileUpdate(files: $files) {
      files {
        id
        fileStatus
        alt
        createdAt
        ... on Video {
          sources {
            url
            width
            height
          }
        }
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
        "id": "gid://shopify/Video/1072273830",
        "alt": "Product demonstration video showing step-by-step assembly instructions and safety guidelines"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "fileUpdate": {
      "files": [
        {
          "id": "gid://shopify/Video/1072273830",
          "fileStatus": "READY",
          "alt": "Product demonstration video showing step-by-step assembly instructions and safety guidelines",
          "createdAt": "2025-06-22T09:19:03Z",
          "sources": [
            {
              "url": "https://cdn.shopify.com/videos/:/vp/some_hash/some_other_hash.m3u8",
              "width": 1280,
              "height": 720
            },
            {
              "url": "https://cdn.shopify.com/videos/c/vp/some_hash/some_other_hash.HD-720p-4.5Mbps.mp4",
              "width": 1280,
              "height": 720
            },
            {
              "url": "https://cdn.shopify.com/videos/c/vp/some_hash/some_other_hash.SD-480p-1.5Mbps.mp4",
              "width": 854,
              "height": 480
            }
          ]
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### fileUpdate reference
