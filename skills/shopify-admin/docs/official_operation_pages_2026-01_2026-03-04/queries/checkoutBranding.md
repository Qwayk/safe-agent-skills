---
title: checkoutBranding - GraphQL Admin
description: >-
  Returns the visual customizations for checkout for a given [checkout
  profile](https://shopify.dev/docs/api/admin-graphql/latest/objects/CheckoutProfile).


  To update checkout branding settings, use the
  [`checkoutBrandingUpsert`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/checkoutBrandingUpsert)
  mutation. Learn more about [customizing checkout's
  appearance](https://shopify.dev/docs/apps/build/checkout/styling).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/checkoutBranding'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/checkoutBranding.md
---

# checkout​Branding

query

Returns the visual customizations for checkout for a given [checkout profile](https://shopify.dev/docs/api/admin-graphql/latest/objects/CheckoutProfile).

To update checkout branding settings, use the [`checkoutBrandingUpsert`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/checkoutBrandingUpsert) mutation. Learn more about [customizing checkout's appearance](https://shopify.dev/docs/apps/build/checkout/styling).

## Arguments

* checkout​Profile​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  A globally-unique identifier.

***

## Possible returns

* Checkout​Branding

  [Checkout​Branding](https://shopify.dev/docs/api/admin-graphql/latest/objects/CheckoutBranding)

  Creates a unified visual identity for your checkout that keeps customers engaged and reinforces your brand throughout the purchase process. This comprehensive branding system lets you control every visual aspect of checkout, from colors and fonts to layouts and imagery, so your checkout feels like a natural extension of your store.

  For example, a luxury fashion retailer can configure their checkout with custom color palettes, premium typography, rounded corners for a softer feel, and branded imagery that matches their main website aesthetic.

  Use the `Branding` object to:

  * Configure comprehensive checkout visual identity
  * Coordinate color schemes across all checkout elements
  * Apply consistent typography and spacing standards
  * Manage background imagery and layout customizations
  * Control visibility of various checkout components

  The branding configuration includes design system foundations like color roles, typography scales, and spacing units, plus specific customizations for sections, dividers, and interactive elements. This allows merchants to create cohesive checkout experiences that reinforce their brand identity while maintaining usability standards.

  Different color schemes can be defined for various contexts, ensuring optimal contrast and accessibility across different checkout states and customer preferences.

  * customizations

    [Checkout​Branding​Customizations](https://shopify.dev/docs/api/admin-graphql/latest/objects/CheckoutBrandingCustomizations)

    The customizations that apply to specific components or areas of the user interface.

  * design​System

    [Checkout​Branding​Design​System](https://shopify.dev/docs/api/admin-graphql/latest/objects/CheckoutBrandingDesignSystem)

    The design system allows you to set values that represent specific attributes of your brand like color and font. These attributes are used throughout the user interface. This brings consistency and allows you to easily make broad design changes.

***

## Examples

* ### Get global colors

  #### Description

  This example demonstrates how to read the global colors from a checkout profile.

  #### Query

  ```graphql
  query GetGlobalColors {
    checkoutBranding(checkoutProfileId: "gid://shopify/CheckoutProfile/235093654") {
      designSystem {
        colors {
          global {
            success
            warning
            critical
            info
            brand
            accent
            decorative
          }
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
  "query": "query GetGlobalColors { checkoutBranding(checkoutProfileId: \"gid://shopify/CheckoutProfile/235093654\") { designSystem { colors { global { success warning critical info brand accent decorative } } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query GetGlobalColors {
      checkoutBranding(checkoutProfileId: "gid://shopify/CheckoutProfile/235093654") {
        designSystem {
          colors {
            global {
              success
              warning
              critical
              info
              brand
              accent
              decorative
            }
          }
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
    query GetGlobalColors {
      checkoutBranding(checkoutProfileId: "gid://shopify/CheckoutProfile/235093654") {
        designSystem {
          colors {
            global {
              success
              warning
              critical
              info
              brand
              accent
              decorative
            }
          }
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
    data: `query GetGlobalColors {
      checkoutBranding(checkoutProfileId: "gid://shopify/CheckoutProfile/235093654") {
        designSystem {
          colors {
            global {
              success
              warning
              critical
              info
              brand
              accent
              decorative
            }
          }
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query GetGlobalColors {
    checkoutBranding(checkoutProfileId: "gid://shopify/CheckoutProfile/235093654") {
      designSystem {
        colors {
          global {
            success
            warning
            critical
            info
            brand
            accent
            decorative
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "checkoutBranding": {
      "designSystem": {
        "colors": {
          "global": {
            "success": "#FFFFFF",
            "warning": "#F0F0F0",
            "critical": "#AABBCC",
            "info": "#ABCDAB",
            "brand": "#ABCDAB",
            "accent": "#0F0F0F",
            "decorative": "#1F2928"
          }
        }
      }
    }
  }
  ```
