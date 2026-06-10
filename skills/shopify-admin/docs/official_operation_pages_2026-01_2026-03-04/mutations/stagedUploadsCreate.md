---
title: stagedUploadsCreate - GraphQL Admin
description: >-
  Creates staged upload targets for file uploads such as images, videos, and 3D
  models.


  Use the `stagedUploadsCreate` mutation instead of direct file creation
  mutations when:


  - **Uploading large files**: Files over a few MB benefit from staged uploads
  for better reliability

  - **Uploading media files**: Videos, 3D models, and high-resolution images

  - **Bulk importing**: CSV files, product catalogs, or other bulk data

  - **Using external file sources**: When files are stored remotely and need to
  be transferred to Shopify


  The `stagedUploadsCreate` mutation is the first step in Shopify's secure
  two-step upload process:


  **Step 1: Create staged upload targets** (this mutation)

  - Generate secure, temporary upload URLs for your files.

  - Receive authentication parameters for the upload.


  **Step 2: Upload files and create assets**

  - Upload your files directly to the provided URLs using the authentication
  parameters.

  - Use the returned `resourceUrl` as the `originalSource` in subsequent
  mutations like `fileCreate`.


  This approach provides better performance for large files, handles network
  interruptions gracefully,

  and ensures secure file transfers to Shopify's storage infrastructure.


  > Note:

  > File size is required when uploading

  >
  [`VIDEO`](https://shopify.dev/docs/api/admin-graphql/latest/enums/StagedUploadTargetGenerateUploadResource#enums-VIDEO)
  or

  >
  [`MODEL_3D`](https://shopify.dev/docs/api/admin-graphql/latest/enums/StagedUploadTargetGenerateUploadResource#enums-MODEL_3D)

  > resources.


  After creating staged upload targets, complete the process by:


  1. **Uploading files**: Send your files to the returned
  [`url`](https://shopify.dev/docs/api/admin-graphql/latest/objects/StagedMediaUploadTarget#field-StagedMediaUploadTarget.fields.url)
  using the provided

  [`parameters`](https://shopify.dev/docs/api/admin-graphql/latest/objects/StagedMediaUploadTarget#field-StagedMediaUploadTarget.fields.parameters)

  for authentication

  2. **Creating file assets**: Use the
  [`resourceUrl`](https://shopify.dev/docs/api/admin-graphql/latest/objects/StagedMediaUploadTarget#field-StagedMediaUploadTarget.fields.resourceUrl)

  as the `originalSource` in mutations such as:
     - [`fileCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/fileCreate):
       Creates file assets from staged uploads
     - [`productUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productUpdate):
       Updates products with new media from staged uploads

  Learn more about [uploading media to
  Shopify](https://shopify.dev/apps/online-store/media/products).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/stagedUploadsCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/stagedUploadsCreate.md
---

# staged​Uploads​Create

mutation

Creates staged upload targets for file uploads such as images, videos, and 3D models.

Use the `stagedUploadsCreate` mutation instead of direct file creation mutations when:

* **Uploading large files**: Files over a few MB benefit from staged uploads for better reliability
* **Uploading media files**: Videos, 3D models, and high-resolution images
* **Bulk importing**: CSV files, product catalogs, or other bulk data
* **Using external file sources**: When files are stored remotely and need to be transferred to Shopify

The `stagedUploadsCreate` mutation is the first step in Shopify's secure two-step upload process:

**Step 1: Create staged upload targets** (this mutation)

* Generate secure, temporary upload URLs for your files.
* Receive authentication parameters for the upload.

**Step 2: Upload files and create assets**

* Upload your files directly to the provided URLs using the authentication parameters.
* Use the returned `resourceUrl` as the `originalSource` in subsequent mutations like `fileCreate`.

This approach provides better performance for large files, handles network interruptions gracefully, and ensures secure file transfers to Shopify's storage infrastructure.

***

**Note:** File size is required when uploading \<a href="https://shopify.dev/docs/api/admin-graphql/latest/enums/StagedUploadTargetGenerateUploadResource#enums-VIDEO">\<code>\<span class="PreventFireFoxApplyingGapToWBR">V\<wbr/>I\<wbr/>D\<wbr/>E\<wbr/>O\</span>\</code>\</a> or \<a href="https://shopify.dev/docs/api/admin-graphql/latest/enums/StagedUploadTargetGenerateUploadResource#enums-MODEL\_3D">\<code>\<span class="PreventFireFoxApplyingGapToWBR">M\<wbr/>O\<wbr/>D\<wbr/>E\<wbr/>L\<wbr/>\_3\<wbr/>D\</span>\</code>\</a> resources.

***

After creating staged upload targets, complete the process by:

1. **Uploading files**: Send your files to the returned [`url`](https://shopify.dev/docs/api/admin-graphql/latest/objects/StagedMediaUploadTarget#field-StagedMediaUploadTarget.fields.url) using the provided [`parameters`](https://shopify.dev/docs/api/admin-graphql/latest/objects/StagedMediaUploadTarget#field-StagedMediaUploadTarget.fields.parameters) for authentication

2. **Creating file assets**: Use the [`resourceUrl`](https://shopify.dev/docs/api/admin-graphql/latest/objects/StagedMediaUploadTarget#field-StagedMediaUploadTarget.fields.resourceUrl) as the `originalSource` in mutations such as:

   * [`fileCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/fileCreate): Creates file assets from staged uploads
   * [`productUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productUpdate): Updates products with new media from staged uploads

Learn more about [uploading media to Shopify](https://shopify.dev/apps/online-store/media/products).

## Arguments

* input

  [\[Staged​Upload​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/StagedUploadInput)

  required

  The information required to generate staged upload targets.

***

## Staged​Uploads​Create​Payload returns

* staged​Targets

  [\[Staged​Media​Upload​Target!\]](https://shopify.dev/docs/api/admin-graphql/latest/objects/StagedMediaUploadTarget)

  The staged upload targets that were generated.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create staged upload targets for a product media gallery

  #### Description

  Create staged upload targets for building a comprehensive product media gallery with images, videos, and 3D models. This example demonstrates creating upload targets for multiple media types that will be used in product galleries. The mutation returns upload URLs, resource URLs for accessing the files after upload, and all necessary \[\`parameters\`]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/StagedMediaUploadTarget#field-StagedMediaUploadTarget.fields.parameters) for the upload process. Each target includes the upload endpoint, form parameters, and resource URLs for subsequent file operations. Learn more about \[managing media for products]\(https://shopify.dev/docs/apps/build/online-store/product-media) and \[uploading files]\(https://help.shopify.com/manual/shopify-admin/productivity-tools/file-uploads).

  #### Query

  ```graphql
  mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
    stagedUploadsCreate(input: $input) {
      stagedTargets {
        url
        resourceUrl
        parameters {
          name
          value
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
    "input": [
      {
        "filename": "product-hero-image.jpg",
        "mimeType": "image/jpeg",
        "httpMethod": "POST",
        "resource": "PRODUCT_IMAGE"
      },
      {
        "filename": "product-demo.mp4",
        "mimeType": "video/mp4",
        "fileSize": "2048000",
        "resource": "VIDEO"
      },
      {
        "filename": "product-model.glb",
        "mimeType": "model/gltf-binary",
        "fileSize": "512000",
        "resource": "MODEL_3D"
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
  "query": "mutation stagedUploadsCreate($input: [StagedUploadInput!]!) { stagedUploadsCreate(input: $input) { stagedTargets { url resourceUrl parameters { name value } } userErrors { field message } } }",
   "variables": {
      "input": [
        {
          "filename": "product-hero-image.jpg",
          "mimeType": "image/jpeg",
          "httpMethod": "POST",
          "resource": "PRODUCT_IMAGE"
        },
        {
          "filename": "product-demo.mp4",
          "mimeType": "video/mp4",
          "fileSize": "2048000",
          "resource": "VIDEO"
        },
        {
          "filename": "product-model.glb",
          "mimeType": "model/gltf-binary",
          "fileSize": "512000",
          "resource": "MODEL_3D"
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
    mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
      stagedUploadsCreate(input: $input) {
        stagedTargets {
          url
          resourceUrl
          parameters {
            name
            value
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
          "input": [
              {
                  "filename": "product-hero-image.jpg",
                  "mimeType": "image/jpeg",
                  "httpMethod": "POST",
                  "resource": "PRODUCT_IMAGE"
              },
              {
                  "filename": "product-demo.mp4",
                  "mimeType": "video/mp4",
                  "fileSize": "2048000",
                  "resource": "VIDEO"
              },
              {
                  "filename": "product-model.glb",
                  "mimeType": "model/gltf-binary",
                  "fileSize": "512000",
                  "resource": "MODEL_3D"
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
    mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
      stagedUploadsCreate(input: $input) {
        stagedTargets {
          url
          resourceUrl
          parameters {
            name
            value
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
    "input": [
      {
        "filename": "product-hero-image.jpg",
        "mimeType": "image/jpeg",
        "httpMethod": "POST",
        "resource": "PRODUCT_IMAGE"
      },
      {
        "filename": "product-demo.mp4",
        "mimeType": "video/mp4",
        "fileSize": "2048000",
        "resource": "VIDEO"
      },
      {
        "filename": "product-model.glb",
        "mimeType": "model/gltf-binary",
        "fileSize": "512000",
        "resource": "MODEL_3D"
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
      "query": `mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
        stagedUploadsCreate(input: $input) {
          stagedTargets {
            url
            resourceUrl
            parameters {
              name
              value
            }
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "input": [
              {
                  "filename": "product-hero-image.jpg",
                  "mimeType": "image/jpeg",
                  "httpMethod": "POST",
                  "resource": "PRODUCT_IMAGE"
              },
              {
                  "filename": "product-demo.mp4",
                  "mimeType": "video/mp4",
                  "fileSize": "2048000",
                  "resource": "VIDEO"
              },
              {
                  "filename": "product-model.glb",
                  "mimeType": "model/gltf-binary",
                  "fileSize": "512000",
                  "resource": "MODEL_3D"
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
  'mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
    stagedUploadsCreate(input: $input) {
      stagedTargets {
        url
        resourceUrl
        parameters {
          name
          value
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
    "input": [
      {
        "filename": "product-hero-image.jpg",
        "mimeType": "image/jpeg",
        "httpMethod": "POST",
        "resource": "PRODUCT_IMAGE"
      },
      {
        "filename": "product-demo.mp4",
        "mimeType": "video/mp4",
        "fileSize": "2048000",
        "resource": "VIDEO"
      },
      {
        "filename": "product-model.glb",
        "mimeType": "model/gltf-binary",
        "fileSize": "512000",
        "resource": "MODEL_3D"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "stagedUploadsCreate": {
      "stagedTargets": [
        {
          "url": "https://snowdevil.myshopify.com/admin/tmp/files",
          "resourceUrl": "https://snowdevil.myshopify.com/admin/tmp/files",
          "parameters": [
            {
              "name": "filename",
              "value": "product-hero-image.jpg"
            },
            {
              "name": "mime_type",
              "value": "image/jpeg"
            },
            {
              "name": "key",
              "value": "tmp/26371970/products/9dd0ad3b-38b0-453a-ba73-b647480faaf8/product-hero-image.jpg"
            }
          ]
        },
        {
          "url": "http://upload.example.com/video-target",
          "resourceUrl": "http://upload.example.com/video-target?external_video_id=25",
          "parameters": [
            {
              "name": "GoogleAccessId",
              "value": "video-development@video-production123.iam.gserviceaccount.com"
            },
            {
              "name": "key",
              "value": "dev/o/v/product-demo.mp4"
            },
            {
              "name": "policy",
              "value": "abc123"
            },
            {
              "name": "signature",
              "value": "abc123"
            }
          ]
        },
        {
          "url": "http://upload.example.com/model-target/dev/o/v/product-model.glb?external_model3d_id=25",
          "resourceUrl": "http://upload.example.com/model-target/dev/o/v/product-model.glb?external_model3d_id=25",
          "parameters": [
            {
              "name": "GoogleAccessId",
              "value": "video-development@video-production123.iam.gserviceaccount.com"
            },
            {
              "name": "key",
              "value": "dev/o/v/product-model.glb"
            },
            {
              "name": "policy",
              "value": "abc123"
            },
            {
              "name": "signature",
              "value": "abc123"
            }
          ]
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### Create staged upload targets for different resource types

  #### Description

  Create \[staged media upload targets]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/StagedMediaUploadTarget) for different resource types including collection images, shop images, and URL redirect imports. This example demonstrates the flexibility of the staged upload system across various Shopify features and workflows. Each resource type has specific requirements and permissions, and the response includes all necessary upload parameters. The resource URLs allow you to access and manage the uploaded files within their respective contexts.

  #### Query

  ```graphql
  mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
    stagedUploadsCreate(input: $input) {
      stagedTargets {
        url
        resourceUrl
        parameters {
          name
          value
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
    "input": [
      {
        "filename": "collection-banner.jpg",
        "mimeType": "image/jpeg",
        "resource": "COLLECTION_IMAGE",
        "httpMethod": "POST"
      },
      {
        "filename": "logo-update.png",
        "mimeType": "image/png",
        "resource": "SHOP_IMAGE",
        "httpMethod": "POST"
      },
      {
        "filename": "url-redirects.csv",
        "mimeType": "text/csv",
        "resource": "URL_REDIRECT_IMPORT",
        "httpMethod": "POST"
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
  "query": "mutation stagedUploadsCreate($input: [StagedUploadInput!]!) { stagedUploadsCreate(input: $input) { stagedTargets { url resourceUrl parameters { name value } } userErrors { field message } } }",
   "variables": {
      "input": [
        {
          "filename": "collection-banner.jpg",
          "mimeType": "image/jpeg",
          "resource": "COLLECTION_IMAGE",
          "httpMethod": "POST"
        },
        {
          "filename": "logo-update.png",
          "mimeType": "image/png",
          "resource": "SHOP_IMAGE",
          "httpMethod": "POST"
        },
        {
          "filename": "url-redirects.csv",
          "mimeType": "text/csv",
          "resource": "URL_REDIRECT_IMPORT",
          "httpMethod": "POST"
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
    mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
      stagedUploadsCreate(input: $input) {
        stagedTargets {
          url
          resourceUrl
          parameters {
            name
            value
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
          "input": [
              {
                  "filename": "collection-banner.jpg",
                  "mimeType": "image/jpeg",
                  "resource": "COLLECTION_IMAGE",
                  "httpMethod": "POST"
              },
              {
                  "filename": "logo-update.png",
                  "mimeType": "image/png",
                  "resource": "SHOP_IMAGE",
                  "httpMethod": "POST"
              },
              {
                  "filename": "url-redirects.csv",
                  "mimeType": "text/csv",
                  "resource": "URL_REDIRECT_IMPORT",
                  "httpMethod": "POST"
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
    mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
      stagedUploadsCreate(input: $input) {
        stagedTargets {
          url
          resourceUrl
          parameters {
            name
            value
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
    "input": [
      {
        "filename": "collection-banner.jpg",
        "mimeType": "image/jpeg",
        "resource": "COLLECTION_IMAGE",
        "httpMethod": "POST"
      },
      {
        "filename": "logo-update.png",
        "mimeType": "image/png",
        "resource": "SHOP_IMAGE",
        "httpMethod": "POST"
      },
      {
        "filename": "url-redirects.csv",
        "mimeType": "text/csv",
        "resource": "URL_REDIRECT_IMPORT",
        "httpMethod": "POST"
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
      "query": `mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
        stagedUploadsCreate(input: $input) {
          stagedTargets {
            url
            resourceUrl
            parameters {
              name
              value
            }
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "input": [
              {
                  "filename": "collection-banner.jpg",
                  "mimeType": "image/jpeg",
                  "resource": "COLLECTION_IMAGE",
                  "httpMethod": "POST"
              },
              {
                  "filename": "logo-update.png",
                  "mimeType": "image/png",
                  "resource": "SHOP_IMAGE",
                  "httpMethod": "POST"
              },
              {
                  "filename": "url-redirects.csv",
                  "mimeType": "text/csv",
                  "resource": "URL_REDIRECT_IMPORT",
                  "httpMethod": "POST"
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
  'mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
    stagedUploadsCreate(input: $input) {
      stagedTargets {
        url
        resourceUrl
        parameters {
          name
          value
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
    "input": [
      {
        "filename": "collection-banner.jpg",
        "mimeType": "image/jpeg",
        "resource": "COLLECTION_IMAGE",
        "httpMethod": "POST"
      },
      {
        "filename": "logo-update.png",
        "mimeType": "image/png",
        "resource": "SHOP_IMAGE",
        "httpMethod": "POST"
      },
      {
        "filename": "url-redirects.csv",
        "mimeType": "text/csv",
        "resource": "URL_REDIRECT_IMPORT",
        "httpMethod": "POST"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "stagedUploadsCreate": {
      "stagedTargets": [
        {
          "url": "https://snowdevil.myshopify.com/admin/tmp/files",
          "resourceUrl": "https://snowdevil.myshopify.com/admin/tmp/files",
          "parameters": [
            {
              "name": "filename",
              "value": "collection-banner.jpg"
            },
            {
              "name": "mime_type",
              "value": "image/jpeg"
            },
            {
              "name": "key",
              "value": "tmp/26371970/collections/a995e8bd-7de1-45a0-8821-e59864076603/collection-banner.jpg"
            }
          ]
        },
        {
          "url": "https://snowdevil.myshopify.com/admin/tmp/files",
          "resourceUrl": "https://snowdevil.myshopify.com/admin/tmp/files",
          "parameters": [
            {
              "name": "filename",
              "value": "logo-update.png"
            },
            {
              "name": "mime_type",
              "value": "image/png"
            },
            {
              "name": "key",
              "value": "tmp/26371970/files/13f1ff20-8d21-434d-bf40-e7a41ffd1124/logo-update.png"
            }
          ]
        },
        {
          "url": "https://snowdevil.myshopify.com/admin/tmp/files",
          "resourceUrl": "https://snowdevil.myshopify.com/admin/tmp/files",
          "parameters": [
            {
              "name": "filename",
              "value": "url-redirects.csv"
            },
            {
              "name": "mime_type",
              "value": "text/csv"
            },
            {
              "name": "key",
              "value": "tmp/26371970/redirect_imports/491a8a08-582b-4b11-81c4-9bf6c920cfd0/url-redirects.csv"
            }
          ]
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### Handle staged upload validation errors and failures

  #### Description

  Handle common validation errors when creating staged upload targets, including unsupported file types and invalid filenames. This example shows how the mutation responds to problematic input with detailed error messages and field-specific error codes. The response includes both successful \[targets]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/StagedMediaUploadTarget) and detailed error information for failed requests.

  #### Query

  ```graphql
  mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
    stagedUploadsCreate(input: $input) {
      stagedTargets {
        url
        resourceUrl
        parameters {
          name
          value
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
    "input": [
      {
        "filename": "valid-image.jpg",
        "mimeType": "image/jpeg",
        "resource": "PRODUCT_IMAGE",
        "httpMethod": "POST"
      },
      {
        "filename": "unsupported-file.xyz",
        "mimeType": "application/xyz",
        "resource": "PRODUCT_IMAGE",
        "httpMethod": "POST"
      },
      {
        "filename": "https://invalid.example.com/filename/with/slashes.jpg",
        "mimeType": "image/jpeg",
        "resource": "PRODUCT_IMAGE",
        "httpMethod": "POST"
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
  "query": "mutation stagedUploadsCreate($input: [StagedUploadInput!]!) { stagedUploadsCreate(input: $input) { stagedTargets { url resourceUrl parameters { name value } } userErrors { field message } } }",
   "variables": {
      "input": [
        {
          "filename": "valid-image.jpg",
          "mimeType": "image/jpeg",
          "resource": "PRODUCT_IMAGE",
          "httpMethod": "POST"
        },
        {
          "filename": "unsupported-file.xyz",
          "mimeType": "application/xyz",
          "resource": "PRODUCT_IMAGE",
          "httpMethod": "POST"
        },
        {
          "filename": "https://invalid.example.com/filename/with/slashes.jpg",
          "mimeType": "image/jpeg",
          "resource": "PRODUCT_IMAGE",
          "httpMethod": "POST"
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
    mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
      stagedUploadsCreate(input: $input) {
        stagedTargets {
          url
          resourceUrl
          parameters {
            name
            value
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
          "input": [
              {
                  "filename": "valid-image.jpg",
                  "mimeType": "image/jpeg",
                  "resource": "PRODUCT_IMAGE",
                  "httpMethod": "POST"
              },
              {
                  "filename": "unsupported-file.xyz",
                  "mimeType": "application/xyz",
                  "resource": "PRODUCT_IMAGE",
                  "httpMethod": "POST"
              },
              {
                  "filename": "https://invalid.example.com/filename/with/slashes.jpg",
                  "mimeType": "image/jpeg",
                  "resource": "PRODUCT_IMAGE",
                  "httpMethod": "POST"
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
    mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
      stagedUploadsCreate(input: $input) {
        stagedTargets {
          url
          resourceUrl
          parameters {
            name
            value
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
    "input": [
      {
        "filename": "valid-image.jpg",
        "mimeType": "image/jpeg",
        "resource": "PRODUCT_IMAGE",
        "httpMethod": "POST"
      },
      {
        "filename": "unsupported-file.xyz",
        "mimeType": "application/xyz",
        "resource": "PRODUCT_IMAGE",
        "httpMethod": "POST"
      },
      {
        "filename": "https://invalid.example.com/filename/with/slashes.jpg",
        "mimeType": "image/jpeg",
        "resource": "PRODUCT_IMAGE",
        "httpMethod": "POST"
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
      "query": `mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
        stagedUploadsCreate(input: $input) {
          stagedTargets {
            url
            resourceUrl
            parameters {
              name
              value
            }
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "input": [
              {
                  "filename": "valid-image.jpg",
                  "mimeType": "image/jpeg",
                  "resource": "PRODUCT_IMAGE",
                  "httpMethod": "POST"
              },
              {
                  "filename": "unsupported-file.xyz",
                  "mimeType": "application/xyz",
                  "resource": "PRODUCT_IMAGE",
                  "httpMethod": "POST"
              },
              {
                  "filename": "https://invalid.example.com/filename/with/slashes.jpg",
                  "mimeType": "image/jpeg",
                  "resource": "PRODUCT_IMAGE",
                  "httpMethod": "POST"
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
  'mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
    stagedUploadsCreate(input: $input) {
      stagedTargets {
        url
        resourceUrl
        parameters {
          name
          value
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
    "input": [
      {
        "filename": "valid-image.jpg",
        "mimeType": "image/jpeg",
        "resource": "PRODUCT_IMAGE",
        "httpMethod": "POST"
      },
      {
        "filename": "unsupported-file.xyz",
        "mimeType": "application/xyz",
        "resource": "PRODUCT_IMAGE",
        "httpMethod": "POST"
      },
      {
        "filename": "https://invalid.example.com/filename/with/slashes.jpg",
        "mimeType": "image/jpeg",
        "resource": "PRODUCT_IMAGE",
        "httpMethod": "POST"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "stagedUploadsCreate": {
      "stagedTargets": [
        {
          "url": "https://snowdevil.myshopify.com/admin/tmp/files",
          "resourceUrl": "https://snowdevil.myshopify.com/admin/tmp/files",
          "parameters": [
            {
              "name": "filename",
              "value": "valid-image.jpg"
            },
            {
              "name": "mime_type",
              "value": "image/jpeg"
            },
            {
              "name": "key",
              "value": "tmp/26371970/products/0fede6f2-195d-44c3-96e9-573c7c863cd1/valid-image.jpg"
            }
          ]
        },
        {
          "url": null,
          "resourceUrl": null,
          "parameters": []
        },
        {
          "url": "https://snowdevil.myshopify.com/admin/tmp/files",
          "resourceUrl": "https://snowdevil.myshopify.com/admin/tmp/files",
          "parameters": [
            {
              "name": "filename",
              "value": "slashes.jpg"
            },
            {
              "name": "mime_type",
              "value": "image/jpeg"
            },
            {
              "name": "key",
              "value": "tmp/26371970/products/0507d1e2-af22-49cb-ab95-c10a4b19c9c0/slashes.jpg"
            }
          ]
        }
      ],
      "userErrors": [
        {
          "field": [
            "input",
            "1",
            "mimeType"
          ],
          "message": "unsupported-file.xyz: (application/xyz) is not a recognized format"
        }
      ]
    }
  }
  ```

* ### stagedUploadsCreate reference
