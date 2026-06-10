---
title: draftOrderUpdate - GraphQL Admin
description: >-
  Updates a draft order.


  If a checkout has been started for a draft order, any update to the draft will
  unlink the checkout. Checkouts

  are created but not immediately completed when opening the merchant credit
  card modal in the admin, and when a

  buyer opens the invoice URL. This is usually fine, but there is an edge case
  where a checkout is in progress

  and the draft is updated before the checkout completes. This will not
  interfere with the checkout and order

  creation, but if the link from draft to checkout is broken the draft will
  remain open even after the order is

  created.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderUpdate'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderUpdate.md
---

# draft​Order​Update

mutation

Requires `write_draft_orders` access scope. Also: The user must have access to manage draft orders.

Updates a draft order.

If a checkout has been started for a draft order, any update to the draft will unlink the checkout. Checkouts are created but not immediately completed when opening the merchant credit card modal in the admin, and when a buyer opens the invoice URL. This is usually fine, but there is an edge case where a checkout is in progress and the draft is updated before the checkout completes. This will not interfere with the checkout and order creation, but if the link from draft to checkout is broken the draft will remain open even after the order is created.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  Specifies the draft order to update.

* input

  [Draft​Order​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/DraftOrderInput)

  required

  The draft order properties to update.

***

## Draft​Order​Update​Payload returns

* draft​Order

  [Draft​Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/DraftOrder)

  The updated draft order.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a new metafield and update another on an existing draft order

  #### Description

  Create a new metafield \`my\_field.delivery\_instructions\` and update an existing metafield \`my\_fields.purchase\_order\` on a specific draft order. Alternatively, refer to the \[metafieldsSet]\(https://shopify.dev/api/admin-graphql/latest/mutations/metafieldsset) mutation to create and/or update metafields on draft order resources.

  #### Query

  ```graphql
  mutation updateDraftOrderMetafields($input: DraftOrderInput!, $ownerId: ID!) {
    draftOrderUpdate(input: $input, id: $ownerId) {
      draftOrder {
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
          "key": "delivery_instructions",
          "type": "single_line_text_field",
          "value": "leave on back porch"
        },
        {
          "id": "gid://shopify/Metafield/1069229059",
          "value": "123"
        }
      ]
    },
    "ownerId": "gid://shopify/DraftOrder/276395349"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation updateDraftOrderMetafields($input: DraftOrderInput!, $ownerId: ID!) { draftOrderUpdate(input: $input, id: $ownerId) { draftOrder { id metafields(first: 3) { edges { node { id namespace key value } } } } userErrors { message field } } }",
   "variables": {
      "input": {
        "metafields": [
          {
            "namespace": "my_field",
            "key": "delivery_instructions",
            "type": "single_line_text_field",
            "value": "leave on back porch"
          },
          {
            "id": "gid://shopify/Metafield/1069229059",
            "value": "123"
          }
        ]
      },
      "ownerId": "gid://shopify/DraftOrder/276395349"
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
    mutation updateDraftOrderMetafields($input: DraftOrderInput!, $ownerId: ID!) {
      draftOrderUpdate(input: $input, id: $ownerId) {
        draftOrder {
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
                      "key": "delivery_instructions",
                      "type": "single_line_text_field",
                      "value": "leave on back porch"
                  },
                  {
                      "id": "gid://shopify/Metafield/1069229059",
                      "value": "123"
                  }
              ]
          },
          "ownerId": "gid://shopify/DraftOrder/276395349"
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
    mutation updateDraftOrderMetafields($input: DraftOrderInput!, $ownerId: ID!) {
      draftOrderUpdate(input: $input, id: $ownerId) {
        draftOrder {
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
          "key": "delivery_instructions",
          "type": "single_line_text_field",
          "value": "leave on back porch"
        },
        {
          "id": "gid://shopify/Metafield/1069229059",
          "value": "123"
        }
      ]
    },
    "ownerId": "gid://shopify/DraftOrder/276395349"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation updateDraftOrderMetafields($input: DraftOrderInput!, $ownerId: ID!) {
        draftOrderUpdate(input: $input, id: $ownerId) {
          draftOrder {
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
                      "key": "delivery_instructions",
                      "type": "single_line_text_field",
                      "value": "leave on back porch"
                  },
                  {
                      "id": "gid://shopify/Metafield/1069229059",
                      "value": "123"
                  }
              ]
          },
          "ownerId": "gid://shopify/DraftOrder/276395349"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation updateDraftOrderMetafields($input: DraftOrderInput!, $ownerId: ID!) {
    draftOrderUpdate(input: $input, id: $ownerId) {
      draftOrder {
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
          "key": "delivery_instructions",
          "type": "single_line_text_field",
          "value": "leave on back porch"
        },
        {
          "id": "gid://shopify/Metafield/1069229059",
          "value": "123"
        }
      ]
    },
    "ownerId": "gid://shopify/DraftOrder/276395349"
  }'
  ```

  #### Response

  ```json
  {
    "draftOrderUpdate": {
      "draftOrder": {
        "id": "gid://shopify/DraftOrder/276395349",
        "metafields": {
          "edges": [
            {
              "node": {
                "id": "gid://shopify/Metafield/1069229059",
                "namespace": "my_fields",
                "key": "purchase_order",
                "value": "123"
              }
            },
            {
              "node": {
                "id": "gid://shopify/Metafield/1069229060",
                "namespace": "my_field",
                "key": "delivery_instructions",
                "value": "leave on back porch"
              }
            }
          ]
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Modify an existing DraftOrder

  #### Query

  ```graphql
  mutation draftOrderUpdate($id: ID!, $input: DraftOrderInput!) {
    draftOrderUpdate(id: $id, input: $input) {
      draftOrder {
        id
        note2
        email
        taxesIncluded
        currencyCode
        invoiceSentAt
        createdAt
        updatedAt
        taxExempt
        completedAt
        name
        status
        marketRegionCountryCode
        presentmentCurrencyCode
        shippingAddress {
          firstName
          address1
          phone
          city
          zip
          province
          country
          lastName
          address2
          company
          latitude
          longitude
          name
          country
          countryCodeV2
          provinceCode
        }
        billingAddress {
          firstName
          address1
          phone
          city
          zip
          province
          country
          lastName
          address2
          company
          latitude
          longitude
          name
          country
          countryCodeV2
          provinceCode
        }
        invoiceUrl
        appliedDiscount {
          title
          value
          valueType
        }
        order {
          id
          customAttributes {
            key
            value
          }
        }
        shippingLine {
          id
          title
          carrierIdentifier
          custom
          code
          deliveryCategory
          source
          discountedPriceSet {
            presentmentMoney {
              amount
              currencyCode
            }
            shopMoney {
              amount
              currencyCode
            }
          }
        }
        taxLines {
          channelLiable
          priceSet {
            presentmentMoney {
              amount
              currencyCode
            }
            shopMoney {
              amount
              currencyCode
            }
          }
          rate
          ratePercentage
          source
          title
        }
        tags
        customer {
          id
          email
          smsMarketingConsent {
            consentCollectedFrom
            consentUpdatedAt
            marketingOptInLevel
            marketingState
          }
          emailMarketingConsent {
            consentUpdatedAt
            marketingOptInLevel
            marketingState
          }
          createdAt
          updatedAt
          firstName
          lastName
          state
          amountSpent {
            amount
            currencyCode
          }
          lastOrder {
            id
            name
            currencyCode
          }
          note
          verifiedEmail
          multipassIdentifier
          taxExempt
          tags
          phone
          taxExemptions
          defaultAddress {
            id
            firstName
            lastName
            company
            address1
            address2
            city
            province
            country
            zip
            phone
            name
            provinceCode
            countryCodeV2
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
    "id": "gid://shopify/DraftOrder/276395349",
    "input": {
      "shippingAddress": {
        "address1": "123 shipping ave",
        "city": "Ottawa",
        "provinceCode": "ON",
        "zip": "K1L 2J3",
        "country": "Canada"
      },
      "marketRegionCountryCode": "CA",
      "presentmentCurrencyCode": "CAD"
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
  "query": "mutation draftOrderUpdate($id: ID!, $input: DraftOrderInput!) { draftOrderUpdate(id: $id, input: $input) { draftOrder { id note2 email taxesIncluded currencyCode invoiceSentAt createdAt updatedAt taxExempt completedAt name status marketRegionCountryCode presentmentCurrencyCode shippingAddress { firstName address1 phone city zip province country lastName address2 company latitude longitude name country countryCodeV2 provinceCode } billingAddress { firstName address1 phone city zip province country lastName address2 company latitude longitude name country countryCodeV2 provinceCode } invoiceUrl appliedDiscount { title value valueType } order { id customAttributes { key value } } shippingLine { id title carrierIdentifier custom code deliveryCategory source discountedPriceSet { presentmentMoney { amount currencyCode } shopMoney { amount currencyCode } } } taxLines { channelLiable priceSet { presentmentMoney { amount currencyCode } shopMoney { amount currencyCode } } rate ratePercentage source title } tags customer { id email smsMarketingConsent { consentCollectedFrom consentUpdatedAt marketingOptInLevel marketingState } emailMarketingConsent { consentUpdatedAt marketingOptInLevel marketingState } createdAt updatedAt firstName lastName state amountSpent { amount currencyCode } lastOrder { id name currencyCode } note verifiedEmail multipassIdentifier taxExempt tags phone taxExemptions defaultAddress { id firstName lastName company address1 address2 city province country zip phone name provinceCode countryCodeV2 } } } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/DraftOrder/276395349",
      "input": {
        "shippingAddress": {
          "address1": "123 shipping ave",
          "city": "Ottawa",
          "provinceCode": "ON",
          "zip": "K1L 2J3",
          "country": "Canada"
        },
        "marketRegionCountryCode": "CA",
        "presentmentCurrencyCode": "CAD"
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
    mutation draftOrderUpdate($id: ID!, $input: DraftOrderInput!) {
      draftOrderUpdate(id: $id, input: $input) {
        draftOrder {
          id
          note2
          email
          taxesIncluded
          currencyCode
          invoiceSentAt
          createdAt
          updatedAt
          taxExempt
          completedAt
          name
          status
          marketRegionCountryCode
          presentmentCurrencyCode
          shippingAddress {
            firstName
            address1
            phone
            city
            zip
            province
            country
            lastName
            address2
            company
            latitude
            longitude
            name
            country
            countryCodeV2
            provinceCode
          }
          billingAddress {
            firstName
            address1
            phone
            city
            zip
            province
            country
            lastName
            address2
            company
            latitude
            longitude
            name
            country
            countryCodeV2
            provinceCode
          }
          invoiceUrl
          appliedDiscount {
            title
            value
            valueType
          }
          order {
            id
            customAttributes {
              key
              value
            }
          }
          shippingLine {
            id
            title
            carrierIdentifier
            custom
            code
            deliveryCategory
            source
            discountedPriceSet {
              presentmentMoney {
                amount
                currencyCode
              }
              shopMoney {
                amount
                currencyCode
              }
            }
          }
          taxLines {
            channelLiable
            priceSet {
              presentmentMoney {
                amount
                currencyCode
              }
              shopMoney {
                amount
                currencyCode
              }
            }
            rate
            ratePercentage
            source
            title
          }
          tags
          customer {
            id
            email
            smsMarketingConsent {
              consentCollectedFrom
              consentUpdatedAt
              marketingOptInLevel
              marketingState
            }
            emailMarketingConsent {
              consentUpdatedAt
              marketingOptInLevel
              marketingState
            }
            createdAt
            updatedAt
            firstName
            lastName
            state
            amountSpent {
              amount
              currencyCode
            }
            lastOrder {
              id
              name
              currencyCode
            }
            note
            verifiedEmail
            multipassIdentifier
            taxExempt
            tags
            phone
            taxExemptions
            defaultAddress {
              id
              firstName
              lastName
              company
              address1
              address2
              city
              province
              country
              zip
              phone
              name
              provinceCode
              countryCodeV2
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
          "id": "gid://shopify/DraftOrder/276395349",
          "input": {
              "shippingAddress": {
                  "address1": "123 shipping ave",
                  "city": "Ottawa",
                  "provinceCode": "ON",
                  "zip": "K1L 2J3",
                  "country": "Canada"
              },
              "marketRegionCountryCode": "CA",
              "presentmentCurrencyCode": "CAD"
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
    mutation draftOrderUpdate($id: ID!, $input: DraftOrderInput!) {
      draftOrderUpdate(id: $id, input: $input) {
        draftOrder {
          id
          note2
          email
          taxesIncluded
          currencyCode
          invoiceSentAt
          createdAt
          updatedAt
          taxExempt
          completedAt
          name
          status
          marketRegionCountryCode
          presentmentCurrencyCode
          shippingAddress {
            firstName
            address1
            phone
            city
            zip
            province
            country
            lastName
            address2
            company
            latitude
            longitude
            name
            country
            countryCodeV2
            provinceCode
          }
          billingAddress {
            firstName
            address1
            phone
            city
            zip
            province
            country
            lastName
            address2
            company
            latitude
            longitude
            name
            country
            countryCodeV2
            provinceCode
          }
          invoiceUrl
          appliedDiscount {
            title
            value
            valueType
          }
          order {
            id
            customAttributes {
              key
              value
            }
          }
          shippingLine {
            id
            title
            carrierIdentifier
            custom
            code
            deliveryCategory
            source
            discountedPriceSet {
              presentmentMoney {
                amount
                currencyCode
              }
              shopMoney {
                amount
                currencyCode
              }
            }
          }
          taxLines {
            channelLiable
            priceSet {
              presentmentMoney {
                amount
                currencyCode
              }
              shopMoney {
                amount
                currencyCode
              }
            }
            rate
            ratePercentage
            source
            title
          }
          tags
          customer {
            id
            email
            smsMarketingConsent {
              consentCollectedFrom
              consentUpdatedAt
              marketingOptInLevel
              marketingState
            }
            emailMarketingConsent {
              consentUpdatedAt
              marketingOptInLevel
              marketingState
            }
            createdAt
            updatedAt
            firstName
            lastName
            state
            amountSpent {
              amount
              currencyCode
            }
            lastOrder {
              id
              name
              currencyCode
            }
            note
            verifiedEmail
            multipassIdentifier
            taxExempt
            tags
            phone
            taxExemptions
            defaultAddress {
              id
              firstName
              lastName
              company
              address1
              address2
              city
              province
              country
              zip
              phone
              name
              provinceCode
              countryCodeV2
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
    "id": "gid://shopify/DraftOrder/276395349",
    "input": {
      "shippingAddress": {
        "address1": "123 shipping ave",
        "city": "Ottawa",
        "provinceCode": "ON",
        "zip": "K1L 2J3",
        "country": "Canada"
      },
      "marketRegionCountryCode": "CA",
      "presentmentCurrencyCode": "CAD"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation draftOrderUpdate($id: ID!, $input: DraftOrderInput!) {
        draftOrderUpdate(id: $id, input: $input) {
          draftOrder {
            id
            note2
            email
            taxesIncluded
            currencyCode
            invoiceSentAt
            createdAt
            updatedAt
            taxExempt
            completedAt
            name
            status
            marketRegionCountryCode
            presentmentCurrencyCode
            shippingAddress {
              firstName
              address1
              phone
              city
              zip
              province
              country
              lastName
              address2
              company
              latitude
              longitude
              name
              country
              countryCodeV2
              provinceCode
            }
            billingAddress {
              firstName
              address1
              phone
              city
              zip
              province
              country
              lastName
              address2
              company
              latitude
              longitude
              name
              country
              countryCodeV2
              provinceCode
            }
            invoiceUrl
            appliedDiscount {
              title
              value
              valueType
            }
            order {
              id
              customAttributes {
                key
                value
              }
            }
            shippingLine {
              id
              title
              carrierIdentifier
              custom
              code
              deliveryCategory
              source
              discountedPriceSet {
                presentmentMoney {
                  amount
                  currencyCode
                }
                shopMoney {
                  amount
                  currencyCode
                }
              }
            }
            taxLines {
              channelLiable
              priceSet {
                presentmentMoney {
                  amount
                  currencyCode
                }
                shopMoney {
                  amount
                  currencyCode
                }
              }
              rate
              ratePercentage
              source
              title
            }
            tags
            customer {
              id
              email
              smsMarketingConsent {
                consentCollectedFrom
                consentUpdatedAt
                marketingOptInLevel
                marketingState
              }
              emailMarketingConsent {
                consentUpdatedAt
                marketingOptInLevel
                marketingState
              }
              createdAt
              updatedAt
              firstName
              lastName
              state
              amountSpent {
                amount
                currencyCode
              }
              lastOrder {
                id
                name
                currencyCode
              }
              note
              verifiedEmail
              multipassIdentifier
              taxExempt
              tags
              phone
              taxExemptions
              defaultAddress {
                id
                firstName
                lastName
                company
                address1
                address2
                city
                province
                country
                zip
                phone
                name
                provinceCode
                countryCodeV2
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
          "id": "gid://shopify/DraftOrder/276395349",
          "input": {
              "shippingAddress": {
                  "address1": "123 shipping ave",
                  "city": "Ottawa",
                  "provinceCode": "ON",
                  "zip": "K1L 2J3",
                  "country": "Canada"
              },
              "marketRegionCountryCode": "CA",
              "presentmentCurrencyCode": "CAD"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation draftOrderUpdate($id: ID!, $input: DraftOrderInput!) {
    draftOrderUpdate(id: $id, input: $input) {
      draftOrder {
        id
        note2
        email
        taxesIncluded
        currencyCode
        invoiceSentAt
        createdAt
        updatedAt
        taxExempt
        completedAt
        name
        status
        marketRegionCountryCode
        presentmentCurrencyCode
        shippingAddress {
          firstName
          address1
          phone
          city
          zip
          province
          country
          lastName
          address2
          company
          latitude
          longitude
          name
          country
          countryCodeV2
          provinceCode
        }
        billingAddress {
          firstName
          address1
          phone
          city
          zip
          province
          country
          lastName
          address2
          company
          latitude
          longitude
          name
          country
          countryCodeV2
          provinceCode
        }
        invoiceUrl
        appliedDiscount {
          title
          value
          valueType
        }
        order {
          id
          customAttributes {
            key
            value
          }
        }
        shippingLine {
          id
          title
          carrierIdentifier
          custom
          code
          deliveryCategory
          source
          discountedPriceSet {
            presentmentMoney {
              amount
              currencyCode
            }
            shopMoney {
              amount
              currencyCode
            }
          }
        }
        taxLines {
          channelLiable
          priceSet {
            presentmentMoney {
              amount
              currencyCode
            }
            shopMoney {
              amount
              currencyCode
            }
          }
          rate
          ratePercentage
          source
          title
        }
        tags
        customer {
          id
          email
          smsMarketingConsent {
            consentCollectedFrom
            consentUpdatedAt
            marketingOptInLevel
            marketingState
          }
          emailMarketingConsent {
            consentUpdatedAt
            marketingOptInLevel
            marketingState
          }
          createdAt
          updatedAt
          firstName
          lastName
          state
          amountSpent {
            amount
            currencyCode
          }
          lastOrder {
            id
            name
            currencyCode
          }
          note
          verifiedEmail
          multipassIdentifier
          taxExempt
          tags
          phone
          taxExemptions
          defaultAddress {
            id
            firstName
            lastName
            company
            address1
            address2
            city
            province
            country
            zip
            phone
            name
            provinceCode
            countryCodeV2
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
    "id": "gid://shopify/DraftOrder/276395349",
    "input": {
      "shippingAddress": {
        "address1": "123 shipping ave",
        "city": "Ottawa",
        "provinceCode": "ON",
        "zip": "K1L 2J3",
        "country": "Canada"
      },
      "marketRegionCountryCode": "CA",
      "presentmentCurrencyCode": "CAD"
    }
  }'
  ```

  #### Response

  ```json
  {
    "draftOrderUpdate": {
      "draftOrder": {
        "id": "gid://shopify/DraftOrder/276395349",
        "note2": "rush order",
        "email": "thomas_burnsimus_ii@shopify.com",
        "taxesIncluded": false,
        "currencyCode": "USD",
        "invoiceSentAt": null,
        "createdAt": "2021-12-01T12:42:15Z",
        "updatedAt": "2024-11-05T17:27:52Z",
        "taxExempt": false,
        "completedAt": null,
        "name": "#D1",
        "status": "OPEN",
        "marketRegionCountryCode": "CA",
        "presentmentCurrencyCode": "CAD",
        "shippingAddress": {
          "firstName": "Bob",
          "address1": "123 shipping ave",
          "phone": "+1(613)555-1212",
          "city": "Ottawa",
          "zip": "K1L 2J3",
          "province": "Ontario",
          "country": "Canada",
          "lastName": "Bobsen",
          "address2": "",
          "company": "",
          "latitude": null,
          "longitude": null,
          "name": "Bob Bobsen",
          "countryCodeV2": "CA",
          "provinceCode": "ON"
        },
        "billingAddress": {
          "firstName": "Bob",
          "address1": "124 Amoebobacterieae St",
          "phone": "+1(343)555-1212",
          "city": "Ottawa",
          "zip": "K2P0V7",
          "province": "Ontario",
          "country": "Canada",
          "lastName": "Bobsen Jr.",
          "address2": "",
          "company": null,
          "latitude": null,
          "longitude": null,
          "name": "Bob Bobsen Jr.",
          "countryCodeV2": "CA",
          "provinceCode": "ON"
        },
        "invoiceUrl": "https://www.snowdevil.ca/26371970/invoices/f1df1a91d10a6d7704cf2f0315461d4d",
        "appliedDiscount": null,
        "order": null,
        "shippingLine": null,
        "taxLines": [
          {
            "channelLiable": null,
            "priceSet": {
              "presentmentMoney": {
                "amount": "5.46",
                "currencyCode": "CAD"
              },
              "shopMoney": {
                "amount": "5.46",
                "currencyCode": "USD"
              }
            },
            "rate": 0.07,
            "ratePercentage": 7,
            "source": null,
            "title": "GST"
          },
          {
            "channelLiable": null,
            "priceSet": {
              "presentmentMoney": {
                "amount": "6.24",
                "currencyCode": "CAD"
              },
              "shopMoney": {
                "amount": "6.24",
                "currencyCode": "USD"
              }
            },
            "rate": 0.08,
            "ratePercentage": 8,
            "source": null,
            "title": "PST"
          }
        ],
        "tags": [
          "Might be fraud"
        ],
        "customer": {
          "id": "gid://shopify/Customer/544365967",
          "email": "bob@example.com",
          "smsMarketingConsent": {
            "consentCollectedFrom": "OTHER",
            "consentUpdatedAt": "2021-06-16T17:31:44Z",
            "marketingOptInLevel": "SINGLE_OPT_IN",
            "marketingState": "SUBSCRIBED"
          },
          "emailMarketingConsent": {
            "consentUpdatedAt": "2005-06-16T15:00:11Z",
            "marketingOptInLevel": "SINGLE_OPT_IN",
            "marketingState": "SUBSCRIBED"
          },
          "createdAt": "2005-06-15T15:57:11Z",
          "updatedAt": "2005-06-16T15:57:11Z",
          "firstName": "Bob",
          "lastName": "Bobsen",
          "state": "ENABLED",
          "amountSpent": {
            "amount": "8305.6",
            "currencyCode": "USD"
          },
          "lastOrder": null,
          "note": null,
          "verifiedEmail": true,
          "multipassIdentifier": null,
          "taxExempt": false,
          "tags": [
            "Bob",
            "Canadian",
            "Léon",
            "Noël"
          ],
          "phone": "+13125551212",
          "taxExemptions": [],
          "defaultAddress": {
            "id": "gid://shopify/MailingAddress/544365967?model_name=CustomerAddress",
            "firstName": "Bob",
            "lastName": "Bobsen",
            "company": "",
            "address1": "123 Amoebobacterieae St",
            "address2": "",
            "city": "Ottawa",
            "province": "Ontario",
            "country": "Canada",
            "zip": "K2P0V6",
            "phone": "+1(613)555-1212",
            "name": "Bob Bobsen",
            "provinceCode": "ON",
            "countryCodeV2": "CA"
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Update the draft order shipping address

  #### Query

  ```graphql
  mutation draftOrderUpdate($id: ID!, $input: DraftOrderInput!) {
    draftOrderUpdate(id: $id, input: $input) {
      draftOrder {
        shippingAddress {
          id
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/DraftOrder/276395349",
    "input": {
      "shippingAddress": {
        "address1": "123 shipping ave",
        "city": "Ottawa",
        "provinceCode": "ON",
        "zip": "K1L 2J3",
        "country": "Canada"
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
  "query": "mutation draftOrderUpdate($id: ID!, $input: DraftOrderInput!) { draftOrderUpdate(id: $id, input: $input) { draftOrder { shippingAddress { id } } } }",
   "variables": {
      "id": "gid://shopify/DraftOrder/276395349",
      "input": {
        "shippingAddress": {
          "address1": "123 shipping ave",
          "city": "Ottawa",
          "provinceCode": "ON",
          "zip": "K1L 2J3",
          "country": "Canada"
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
    mutation draftOrderUpdate($id: ID!, $input: DraftOrderInput!) {
      draftOrderUpdate(id: $id, input: $input) {
        draftOrder {
          shippingAddress {
            id
          }
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/DraftOrder/276395349",
          "input": {
              "shippingAddress": {
                  "address1": "123 shipping ave",
                  "city": "Ottawa",
                  "provinceCode": "ON",
                  "zip": "K1L 2J3",
                  "country": "Canada"
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
    mutation draftOrderUpdate($id: ID!, $input: DraftOrderInput!) {
      draftOrderUpdate(id: $id, input: $input) {
        draftOrder {
          shippingAddress {
            id
          }
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/DraftOrder/276395349",
    "input": {
      "shippingAddress": {
        "address1": "123 shipping ave",
        "city": "Ottawa",
        "provinceCode": "ON",
        "zip": "K1L 2J3",
        "country": "Canada"
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
      "query": `mutation draftOrderUpdate($id: ID!, $input: DraftOrderInput!) {
        draftOrderUpdate(id: $id, input: $input) {
          draftOrder {
            shippingAddress {
              id
            }
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/DraftOrder/276395349",
          "input": {
              "shippingAddress": {
                  "address1": "123 shipping ave",
                  "city": "Ottawa",
                  "provinceCode": "ON",
                  "zip": "K1L 2J3",
                  "country": "Canada"
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
  'mutation draftOrderUpdate($id: ID!, $input: DraftOrderInput!) {
    draftOrderUpdate(id: $id, input: $input) {
      draftOrder {
        shippingAddress {
          id
        }
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/DraftOrder/276395349",
    "input": {
      "shippingAddress": {
        "address1": "123 shipping ave",
        "city": "Ottawa",
        "provinceCode": "ON",
        "zip": "K1L 2J3",
        "country": "Canada"
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "draftOrderUpdate": {
      "draftOrder": {
        "shippingAddress": {
          "id": "gid://shopify/MailingAddress/639215345?model_name=Address"
        }
      }
    }
  }
  ```

* ### Updating a draft order that doesn't exist returns an error

  #### Query

  ```graphql
  mutation draftOrderUpdate($id: ID!, $input: DraftOrderInput!) {
    draftOrderUpdate(id: $id, input: $input) {
      draftOrder {
        id
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
    "id": "gid://shopify/DraftOrder/1",
    "input": {
      "note": "This is a really awesome draft order"
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
  "query": "mutation draftOrderUpdate($id: ID!, $input: DraftOrderInput!) { draftOrderUpdate(id: $id, input: $input) { draftOrder { id } userErrors { message field } } }",
   "variables": {
      "id": "gid://shopify/DraftOrder/1",
      "input": {
        "note": "This is a really awesome draft order"
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
    mutation draftOrderUpdate($id: ID!, $input: DraftOrderInput!) {
      draftOrderUpdate(id: $id, input: $input) {
        draftOrder {
          id
        }
        userErrors {
          message
          field
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/DraftOrder/1",
          "input": {
              "note": "This is a really awesome draft order"
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
    mutation draftOrderUpdate($id: ID!, $input: DraftOrderInput!) {
      draftOrderUpdate(id: $id, input: $input) {
        draftOrder {
          id
        }
        userErrors {
          message
          field
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/DraftOrder/1",
    "input": {
      "note": "This is a really awesome draft order"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation draftOrderUpdate($id: ID!, $input: DraftOrderInput!) {
        draftOrderUpdate(id: $id, input: $input) {
          draftOrder {
            id
          }
          userErrors {
            message
            field
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/DraftOrder/1",
          "input": {
              "note": "This is a really awesome draft order"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation draftOrderUpdate($id: ID!, $input: DraftOrderInput!) {
    draftOrderUpdate(id: $id, input: $input) {
      draftOrder {
        id
      }
      userErrors {
        message
        field
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/DraftOrder/1",
    "input": {
      "note": "This is a really awesome draft order"
    }
  }'
  ```

  #### Response

  ```json
  {
    "draftOrderUpdate": {
      "draftOrder": null,
      "userErrors": [
        {
          "message": "Draft order not found",
          "field": null
        }
      ]
    }
  }
  ```

* ### Updating a draft order with a company, location and company contact

  #### Query

  ```graphql
  mutation draftOrderUpdate($id: ID!, $input: DraftOrderInput!) {
    draftOrderUpdate(id: $id, input: $input) {
      draftOrder {
        purchasingEntity {
          ... on PurchasingCompany {
            company {
              id
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
    "id": "gid://shopify/DraftOrder/276395349",
    "input": {
      "purchasingEntity": {
        "purchasingCompany": {
          "companyId": "gid://shopify/Company/426793626",
          "companyLocationId": "gid://shopify/CompanyLocation/441870438",
          "companyContactId": "gid://shopify/CompanyContact/207808057"
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
  "query": "mutation draftOrderUpdate($id: ID!, $input: DraftOrderInput!) { draftOrderUpdate(id: $id, input: $input) { draftOrder { purchasingEntity { ... on PurchasingCompany { company { id } } } } } }",
   "variables": {
      "id": "gid://shopify/DraftOrder/276395349",
      "input": {
        "purchasingEntity": {
          "purchasingCompany": {
            "companyId": "gid://shopify/Company/426793626",
            "companyLocationId": "gid://shopify/CompanyLocation/441870438",
            "companyContactId": "gid://shopify/CompanyContact/207808057"
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
    mutation draftOrderUpdate($id: ID!, $input: DraftOrderInput!) {
      draftOrderUpdate(id: $id, input: $input) {
        draftOrder {
          purchasingEntity {
            ... on PurchasingCompany {
              company {
                id
              }
            }
          }
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/DraftOrder/276395349",
          "input": {
              "purchasingEntity": {
                  "purchasingCompany": {
                      "companyId": "gid://shopify/Company/426793626",
                      "companyLocationId": "gid://shopify/CompanyLocation/441870438",
                      "companyContactId": "gid://shopify/CompanyContact/207808057"
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
    mutation draftOrderUpdate($id: ID!, $input: DraftOrderInput!) {
      draftOrderUpdate(id: $id, input: $input) {
        draftOrder {
          purchasingEntity {
            ... on PurchasingCompany {
              company {
                id
              }
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/DraftOrder/276395349",
    "input": {
      "purchasingEntity": {
        "purchasingCompany": {
          "companyId": "gid://shopify/Company/426793626",
          "companyLocationId": "gid://shopify/CompanyLocation/441870438",
          "companyContactId": "gid://shopify/CompanyContact/207808057"
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
      "query": `mutation draftOrderUpdate($id: ID!, $input: DraftOrderInput!) {
        draftOrderUpdate(id: $id, input: $input) {
          draftOrder {
            purchasingEntity {
              ... on PurchasingCompany {
                company {
                  id
                }
              }
            }
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/DraftOrder/276395349",
          "input": {
              "purchasingEntity": {
                  "purchasingCompany": {
                      "companyId": "gid://shopify/Company/426793626",
                      "companyLocationId": "gid://shopify/CompanyLocation/441870438",
                      "companyContactId": "gid://shopify/CompanyContact/207808057"
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
  'mutation draftOrderUpdate($id: ID!, $input: DraftOrderInput!) {
    draftOrderUpdate(id: $id, input: $input) {
      draftOrder {
        purchasingEntity {
          ... on PurchasingCompany {
            company {
              id
            }
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/DraftOrder/276395349",
    "input": {
      "purchasingEntity": {
        "purchasingCompany": {
          "companyId": "gid://shopify/Company/426793626",
          "companyLocationId": "gid://shopify/CompanyLocation/441870438",
          "companyContactId": "gid://shopify/CompanyContact/207808057"
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "draftOrderUpdate": {
      "draftOrder": {
        "purchasingEntity": {
          "company": {
            "id": "gid://shopify/Company/426793626"
          }
        }
      }
    }
  }
  ```

* ### draftOrderUpdate reference
