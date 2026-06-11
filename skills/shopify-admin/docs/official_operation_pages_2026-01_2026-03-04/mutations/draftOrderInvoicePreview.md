---
title: draftOrderInvoicePreview - GraphQL Admin
description: Previews a draft order invoice email.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderInvoicePreview
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderInvoicePreview.md
---

# draft​Order​Invoice​Preview

mutation

Requires `write_draft_orders` access scope.

Previews a draft order invoice email.

## Arguments

* email

  [Email​Input](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/EmailInput)

  Specifies the draft order invoice email fields.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  Specifies the draft order invoice email to preview.

***

## Draft​Order​Invoice​Preview​Payload returns

* preview​Html

  [HTML](https://shopify.dev/docs/api/admin-graphql/latest/scalars/HTML)

  The draft order invoice email rendered as HTML to allow previewing.

* preview​Subject

  [HTML](https://shopify.dev/docs/api/admin-graphql/latest/scalars/HTML)

  The subject preview for the draft order invoice email.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Preview a draft order invoice by draft order ID

  #### Query

  ```graphql
  mutation draftOrderInvoicePreview($id: ID!) {
    draftOrderInvoicePreview(id: $id) {
      previewHtml
      previewSubject
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/DraftOrder/276395349"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation draftOrderInvoicePreview($id: ID!) { draftOrderInvoicePreview(id: $id) { previewHtml previewSubject } }",
   "variables": {
      "id": "gid://shopify/DraftOrder/276395349"
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
    mutation draftOrderInvoicePreview($id: ID!) {
      draftOrderInvoicePreview(id: $id) {
        previewHtml
        previewSubject
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/DraftOrder/276395349"
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
    mutation draftOrderInvoicePreview($id: ID!) {
      draftOrderInvoicePreview(id: $id) {
        previewHtml
        previewSubject
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/DraftOrder/276395349"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation draftOrderInvoicePreview($id: ID!) {
        draftOrderInvoicePreview(id: $id) {
          previewHtml
          previewSubject
        }
      }`,
      "variables": {
          "id": "gid://shopify/DraftOrder/276395349"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation draftOrderInvoicePreview($id: ID!) {
    draftOrderInvoicePreview(id: $id) {
      previewHtml
      previewSubject
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/DraftOrder/276395349"
  }'
  ```

  #### Response

  ```json
  {
    "draftOrderInvoicePreview": {
      "previewHtml": "<!DOCTYPE html PUBLIC \"-//W3C//DTD HTML 4.0 Transitional//EN\" \"http://www.w3.org/TR/REC-html40/loose.dtd\">\n<html><body>\n<p>Invoice #D1 from Snowdevil</p>\n<p></p>\n</body></html>\n",
      "previewSubject": "Draft Order #D1"
    }
  }
  ```

* ### Preview a draft order invoice with custom email input

  #### Query

  ```graphql
  mutation draftOrderInvoicePreview($id: ID!, $email: EmailInput) {
    draftOrderInvoicePreview(id: $id, email: $email) {
      previewHtml
      previewSubject
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/DraftOrder/276395349",
    "email": {
      "to": "test@example.com",
      "subject": "Custom subject",
      "customMessage": "Hi,\nThis is a custom message for the customer."
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
  "query": "mutation draftOrderInvoicePreview($id: ID!, $email: EmailInput) { draftOrderInvoicePreview(id: $id, email: $email) { previewHtml previewSubject } }",
   "variables": {
      "id": "gid://shopify/DraftOrder/276395349",
      "email": {
        "to": "test@example.com",
        "subject": "Custom subject",
        "customMessage": "Hi,\nThis is a custom message for the customer."
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
    mutation draftOrderInvoicePreview($id: ID!, $email: EmailInput) {
      draftOrderInvoicePreview(id: $id, email: $email) {
        previewHtml
        previewSubject
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/DraftOrder/276395349",
          "email": {
              "to": "test@example.com",
              "subject": "Custom subject",
              "customMessage": "Hi,\nThis is a custom message for the customer."
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
    mutation draftOrderInvoicePreview($id: ID!, $email: EmailInput) {
      draftOrderInvoicePreview(id: $id, email: $email) {
        previewHtml
        previewSubject
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/DraftOrder/276395349",
    "email": {
      "to": "test@example.com",
      "subject": "Custom subject",
      "customMessage": "Hi,\nThis is a custom message for the customer."
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation draftOrderInvoicePreview($id: ID!, $email: EmailInput) {
        draftOrderInvoicePreview(id: $id, email: $email) {
          previewHtml
          previewSubject
        }
      }`,
      "variables": {
          "id": "gid://shopify/DraftOrder/276395349",
          "email": {
              "to": "test@example.com",
              "subject": "Custom subject",
              "customMessage": "Hi,\nThis is a custom message for the customer."
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation draftOrderInvoicePreview($id: ID!, $email: EmailInput) {
    draftOrderInvoicePreview(id: $id, email: $email) {
      previewHtml
      previewSubject
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/DraftOrder/276395349",
    "email": {
      "to": "test@example.com",
      "subject": "Custom subject",
      "customMessage": "Hi,\nThis is a custom message for the customer."
    }
  }'
  ```

  #### Response

  ```json
  {
    "draftOrderInvoicePreview": {
      "previewHtml": "<!DOCTYPE html PUBLIC \"-//W3C//DTD HTML 4.0 Transitional//EN\" \"http://www.w3.org/TR/REC-html40/loose.dtd\">\n<html><body>\n<p>Invoice #D1 from Snowdevil</p>\n<p>Hi,<br>This is a custom message for the customer.</p>\n</body></html>\n",
      "previewSubject": "Custom subject"
    }
  }
  ```

* ### Previewing a completed draft order returns an error

  #### Query

  ```graphql
  mutation draftOrderInvoicePreview($id: ID!) {
    draftOrderInvoicePreview(id: $id) {
      previewHtml
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
    "id": "gid://shopify/DraftOrder/989355118"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation draftOrderInvoicePreview($id: ID!) { draftOrderInvoicePreview(id: $id) { previewHtml userErrors { message field } } }",
   "variables": {
      "id": "gid://shopify/DraftOrder/989355118"
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
    mutation draftOrderInvoicePreview($id: ID!) {
      draftOrderInvoicePreview(id: $id) {
        previewHtml
        userErrors {
          message
          field
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/DraftOrder/989355118"
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
    mutation draftOrderInvoicePreview($id: ID!) {
      draftOrderInvoicePreview(id: $id) {
        previewHtml
        userErrors {
          message
          field
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/DraftOrder/989355118"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation draftOrderInvoicePreview($id: ID!) {
        draftOrderInvoicePreview(id: $id) {
          previewHtml
          userErrors {
            message
            field
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/DraftOrder/989355118"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation draftOrderInvoicePreview($id: ID!) {
    draftOrderInvoicePreview(id: $id) {
      previewHtml
      userErrors {
        message
        field
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/DraftOrder/989355118"
  }'
  ```

  #### Response

  ```json
  {
    "draftOrderInvoicePreview": {
      "previewHtml": null,
      "userErrors": [
        {
          "message": "Draft order Invoice can't be sent. This draft order is already paid.",
          "field": null
        }
      ]
    }
  }
  ```

* ### draftOrderInvoicePreview reference
