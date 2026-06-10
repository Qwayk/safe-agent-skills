---
title: draftOrderInvoiceSend - GraphQL Admin
description: >-
  Sends an invoice email for a
  [`DraftOrder`](https://shopify.dev/docs/api/admin-graphql/latest/objects/DraftOrder).
  The invoice includes a secure checkout link for reviewing and paying for the
  order. Use the
  [`email`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderInvoiceSend#arguments-email)
  argument to customize the email, such as the subject and message.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderInvoiceSend
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderInvoiceSend.md
---

# draft​Order​Invoice​Send

mutation

Requires `write_draft_orders` access scope. Also: The user must have access to manage draft orders.

Sends an invoice email for a [`DraftOrder`](https://shopify.dev/docs/api/admin-graphql/latest/objects/DraftOrder). The invoice includes a secure checkout link for reviewing and paying for the order. Use the [`email`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderInvoiceSend#arguments-email) argument to customize the email, such as the subject and message.

## Arguments

* email

  [Email​Input](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/EmailInput)

  Specifies the draft order invoice email fields.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  Specifies the draft order to send the invoice for.

***

## Draft​Order​Invoice​Send​Payload returns

* draft​Order

  [Draft​Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/DraftOrder)

  The draft order an invoice email is sent for.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Send a draft order invoice by draft order ID

  #### Query

  ```graphql
  mutation draftOrderInvoiceSend($id: ID!) {
    draftOrderInvoiceSend(id: $id) {
      draftOrder {
        id
      }
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
  "query": "mutation draftOrderInvoiceSend($id: ID!) { draftOrderInvoiceSend(id: $id) { draftOrder { id } } }",
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
    mutation draftOrderInvoiceSend($id: ID!) {
      draftOrderInvoiceSend(id: $id) {
        draftOrder {
          id
        }
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
    mutation draftOrderInvoiceSend($id: ID!) {
      draftOrderInvoiceSend(id: $id) {
        draftOrder {
          id
        }
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
      "query": `mutation draftOrderInvoiceSend($id: ID!) {
        draftOrderInvoiceSend(id: $id) {
          draftOrder {
            id
          }
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
  'mutation draftOrderInvoiceSend($id: ID!) {
    draftOrderInvoiceSend(id: $id) {
      draftOrder {
        id
      }
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
    "draftOrderInvoiceSend": {
      "draftOrder": {
        "id": "gid://shopify/DraftOrder/276395349"
      }
    }
  }
  ```

* ### Send an invoice

  #### Query

  ```graphql
  mutation draftOrderInvoiceSend($id: ID!) {
    draftOrderInvoiceSend(id: $id) {
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
        lineItems(first: 10) {
          edges {
            node {
              id
              variant {
                id
                title
              }
              product {
                id
              }
              name
              sku
              vendor
              quantity
              requiresShipping
              taxable
              isGiftCard
              fulfillmentService {
                type
              }
              weight {
                unit
                value
              }
              taxLines {
                title
                source
                rate
                ratePercentage
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
              }
              appliedDiscount {
                title
                value
                valueType
              }
              name
              custom
              id
            }
          }
        }
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
  "query": "mutation draftOrderInvoiceSend($id: ID!) { draftOrderInvoiceSend(id: $id) { draftOrder { id note2 email taxesIncluded currencyCode invoiceSentAt createdAt updatedAt taxExempt completedAt name status lineItems(first: 10) { edges { node { id variant { id title } product { id } name sku vendor quantity requiresShipping taxable isGiftCard fulfillmentService { type } weight { unit value } taxLines { title source rate ratePercentage priceSet { presentmentMoney { amount currencyCode } shopMoney { amount currencyCode } } } appliedDiscount { title value valueType } name custom id } } } shippingAddress { firstName address1 phone city zip province country lastName address2 company latitude longitude name country countryCodeV2 provinceCode } billingAddress { firstName address1 phone city zip province country lastName address2 company latitude longitude name country countryCodeV2 provinceCode } invoiceUrl appliedDiscount { title value valueType } order { id customAttributes { key value } } shippingLine { id title carrierIdentifier custom code deliveryCategory source discountedPriceSet { presentmentMoney { amount currencyCode } shopMoney { amount currencyCode } } } taxLines { channelLiable priceSet { presentmentMoney { amount currencyCode } shopMoney { amount currencyCode } } rate ratePercentage source title } tags customer { id email smsMarketingConsent { consentCollectedFrom consentUpdatedAt marketingOptInLevel marketingState } emailMarketingConsent { consentUpdatedAt marketingOptInLevel marketingState } createdAt updatedAt firstName lastName state amountSpent { amount currencyCode } lastOrder { id name currencyCode } note verifiedEmail multipassIdentifier taxExempt tags phone taxExemptions defaultAddress { id firstName lastName company address1 address2 city province country zip phone name provinceCode countryCodeV2 } } } userErrors { field message } } }",
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
    mutation draftOrderInvoiceSend($id: ID!) {
      draftOrderInvoiceSend(id: $id) {
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
          lineItems(first: 10) {
            edges {
              node {
                id
                variant {
                  id
                  title
                }
                product {
                  id
                }
                name
                sku
                vendor
                quantity
                requiresShipping
                taxable
                isGiftCard
                fulfillmentService {
                  type
                }
                weight {
                  unit
                  value
                }
                taxLines {
                  title
                  source
                  rate
                  ratePercentage
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
                }
                appliedDiscount {
                  title
                  value
                  valueType
                }
                name
                custom
                id
              }
            }
          }
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
    mutation draftOrderInvoiceSend($id: ID!) {
      draftOrderInvoiceSend(id: $id) {
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
          lineItems(first: 10) {
            edges {
              node {
                id
                variant {
                  id
                  title
                }
                product {
                  id
                }
                name
                sku
                vendor
                quantity
                requiresShipping
                taxable
                isGiftCard
                fulfillmentService {
                  type
                }
                weight {
                  unit
                  value
                }
                taxLines {
                  title
                  source
                  rate
                  ratePercentage
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
                }
                appliedDiscount {
                  title
                  value
                  valueType
                }
                name
                custom
                id
              }
            }
          }
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
    "id": "gid://shopify/DraftOrder/276395349"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation draftOrderInvoiceSend($id: ID!) {
        draftOrderInvoiceSend(id: $id) {
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
            lineItems(first: 10) {
              edges {
                node {
                  id
                  variant {
                    id
                    title
                  }
                  product {
                    id
                  }
                  name
                  sku
                  vendor
                  quantity
                  requiresShipping
                  taxable
                  isGiftCard
                  fulfillmentService {
                    type
                  }
                  weight {
                    unit
                    value
                  }
                  taxLines {
                    title
                    source
                    rate
                    ratePercentage
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
                  }
                  appliedDiscount {
                    title
                    value
                    valueType
                  }
                  name
                  custom
                  id
                }
              }
            }
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
          "id": "gid://shopify/DraftOrder/276395349"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation draftOrderInvoiceSend($id: ID!) {
    draftOrderInvoiceSend(id: $id) {
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
        lineItems(first: 10) {
          edges {
            node {
              id
              variant {
                id
                title
              }
              product {
                id
              }
              name
              sku
              vendor
              quantity
              requiresShipping
              taxable
              isGiftCard
              fulfillmentService {
                type
              }
              weight {
                unit
                value
              }
              taxLines {
                title
                source
                rate
                ratePercentage
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
              }
              appliedDiscount {
                title
                value
                valueType
              }
              name
              custom
              id
            }
          }
        }
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
    "id": "gid://shopify/DraftOrder/276395349"
  }'
  ```

  #### Response

  ```json
  {
    "draftOrderInvoiceSend": {
      "draftOrder": {
        "id": "gid://shopify/DraftOrder/276395349",
        "note2": "rush order",
        "email": "thomas_burnsimus_ii@shopify.com",
        "taxesIncluded": false,
        "currencyCode": "USD",
        "invoiceSentAt": "2024-11-05T17:18:09Z",
        "createdAt": "2021-12-01T12:42:15Z",
        "updatedAt": "2024-11-05T17:18:09Z",
        "taxExempt": false,
        "completedAt": null,
        "name": "#D1",
        "status": "INVOICE_SENT",
        "lineItems": {
          "edges": [
            {
              "node": {
                "id": "gid://shopify/DraftOrderLineItem/693579471",
                "variant": {
                  "id": "gid://shopify/ProductVariant/138327650",
                  "title": "Default"
                },
                "product": {
                  "id": "gid://shopify/Product/121709582"
                },
                "name": "Boots - Default",
                "sku": "boots-10",
                "vendor": null,
                "quantity": 2,
                "requiresShipping": true,
                "taxable": true,
                "isGiftCard": false,
                "fulfillmentService": {
                  "type": "MANUAL"
                },
                "weight": {
                  "unit": "GRAMS",
                  "value": 100
                },
                "taxLines": [
                  {
                    "title": "GST",
                    "source": null,
                    "rate": 0.07,
                    "ratePercentage": 7,
                    "priceSet": {
                      "presentmentMoney": {
                        "amount": "4.2",
                        "currencyCode": "USD"
                      },
                      "shopMoney": {
                        "amount": "4.2",
                        "currencyCode": "USD"
                      }
                    }
                  },
                  {
                    "title": "PST",
                    "source": null,
                    "rate": 0.08,
                    "ratePercentage": 8,
                    "priceSet": {
                      "presentmentMoney": {
                        "amount": "4.8",
                        "currencyCode": "USD"
                      },
                      "shopMoney": {
                        "amount": "4.8",
                        "currencyCode": "USD"
                      }
                    }
                  }
                ],
                "appliedDiscount": null,
                "custom": false
              }
            }
          ]
        },
        "shippingAddress": {
          "firstName": "Bob",
          "address1": "123 Amoebobacterieae St",
          "phone": "+1(613)555-1212",
          "city": "Ottawa",
          "zip": "K2P0V6",
          "province": "Ontario",
          "country": "Canada",
          "lastName": "Bobsen",
          "address2": "",
          "company": "",
          "latitude": 45.41634,
          "longitude": -75.6868,
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
                "amount": "4.2",
                "currencyCode": "USD"
              },
              "shopMoney": {
                "amount": "4.2",
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
                "amount": "4.8",
                "currencyCode": "USD"
              },
              "shopMoney": {
                "amount": "4.8",
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

* ### Sending an invoice with invalid arguments returns an error

  #### Query

  ```graphql
  mutation draftOrderInvoiceSend($id: ID!, $email: EmailInput) {
    draftOrderInvoiceSend(id: $id, email: $email) {
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
    "id": "gid://shopify/DraftOrder/276395349",
    "email": {
      "subject": "valid subject",
      "to": "invalid recipient"
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
  "query": "mutation draftOrderInvoiceSend($id: ID!, $email: EmailInput) { draftOrderInvoiceSend(id: $id, email: $email) { draftOrder { id } userErrors { message field } } }",
   "variables": {
      "id": "gid://shopify/DraftOrder/276395349",
      "email": {
        "subject": "valid subject",
        "to": "invalid recipient"
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
    mutation draftOrderInvoiceSend($id: ID!, $email: EmailInput) {
      draftOrderInvoiceSend(id: $id, email: $email) {
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
          "id": "gid://shopify/DraftOrder/276395349",
          "email": {
              "subject": "valid subject",
              "to": "invalid recipient"
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
    mutation draftOrderInvoiceSend($id: ID!, $email: EmailInput) {
      draftOrderInvoiceSend(id: $id, email: $email) {
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
    "id": "gid://shopify/DraftOrder/276395349",
    "email": {
      "subject": "valid subject",
      "to": "invalid recipient"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation draftOrderInvoiceSend($id: ID!, $email: EmailInput) {
        draftOrderInvoiceSend(id: $id, email: $email) {
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
          "id": "gid://shopify/DraftOrder/276395349",
          "email": {
              "subject": "valid subject",
              "to": "invalid recipient"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation draftOrderInvoiceSend($id: ID!, $email: EmailInput) {
    draftOrderInvoiceSend(id: $id, email: $email) {
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
    "id": "gid://shopify/DraftOrder/276395349",
    "email": {
      "subject": "valid subject",
      "to": "invalid recipient"
    }
  }'
  ```

  #### Response

  ```json
  {
    "draftOrderInvoiceSend": {
      "draftOrder": {
        "id": "gid://shopify/DraftOrder/276395349"
      },
      "userErrors": [
        {
          "message": "To is invalid",
          "field": null
        }
      ]
    }
  }
  ```

* ### draftOrderInvoiceSend reference
