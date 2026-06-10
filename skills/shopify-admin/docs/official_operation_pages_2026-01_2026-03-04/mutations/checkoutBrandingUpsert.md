---
title: checkoutBrandingUpsert - GraphQL Admin
description: >-
  Updates the visual branding for a
  [`CheckoutProfile`](https://shopify.dev/docs/api/admin-graphql/latest/objects/CheckoutProfile),
  customizing how checkout displays to customers. Creates new branding settings
  if none exist, or modifies existing settings.


  The mutation accepts two levels of customization through the
  [`CheckoutBrandingInput`](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CheckoutBrandingInput)
  input object.
  [`designSystem`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/checkoutBrandingUpsert#arguments-checkoutBrandingInput.fields.designSystem)
  defines foundational brand attributes like colors, typography, and corner
  radius that apply consistently throughout checkout.
  [`customizations`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/checkoutBrandingUpsert#arguments-checkoutBrandingInput.fields.customizations)
  defines styles for specific parts of the UI, individual components, or groups
  of components like the header, buttons, form fields, and sections.


  Changes to a published checkout profile display immediately in the store's
  checkout. You can preview draft profiles in the Shopify admin's checkout
  editor before publishing.


  Learn more about [checkout
  styling](https://shopify.dev/docs/apps/checkout/styling).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/checkoutBrandingUpsert
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/checkoutBrandingUpsert.md
---

# checkout​Branding​Upsert

mutation

Requires access to checkout branding settings and the shop must be on a Plus plan or a Development store plan. User must have `preferences` permission to modify.

Updates the visual branding for a [`CheckoutProfile`](https://shopify.dev/docs/api/admin-graphql/latest/objects/CheckoutProfile), customizing how checkout displays to customers. Creates new branding settings if none exist, or modifies existing settings.

The mutation accepts two levels of customization through the [`CheckoutBrandingInput`](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CheckoutBrandingInput) input object. [`designSystem`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/checkoutBrandingUpsert#arguments-checkoutBrandingInput.fields.designSystem) defines foundational brand attributes like colors, typography, and corner radius that apply consistently throughout checkout. [`customizations`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/checkoutBrandingUpsert#arguments-checkoutBrandingInput.fields.customizations) defines styles for specific parts of the UI, individual components, or groups of components like the header, buttons, form fields, and sections.

Changes to a published checkout profile display immediately in the store's checkout. You can preview draft profiles in the Shopify admin's checkout editor before publishing.

Learn more about [checkout styling](https://shopify.dev/docs/apps/checkout/styling).

## Arguments

* checkout​Branding​Input

  [Checkout​Branding​Input](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CheckoutBrandingInput)

  The input fields to use to upsert the checkout branding settings (pass null to reset them to default).

* checkout​Profile​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  A globally-unique identifier.

***

## Checkout​Branding​Upsert​Payload returns

* checkout​Branding

  [Checkout​Branding](https://shopify.dev/docs/api/admin-graphql/latest/objects/CheckoutBranding)

  Returns the new checkout branding settings.

* user​Errors

  [\[Checkout​Branding​Upsert​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CheckoutBrandingUpsertUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Apply section styles to main and order summary

  #### Query

  ```graphql
  mutation ApplySectionStyles($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) {
    checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) {
      checkoutBranding {
        customizations {
          main {
            section {
              cornerRadius
              colorScheme
              shadow
              padding
            }
          }
          orderSummary {
            section {
              colorScheme
              shadow
              padding
              border
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
    "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
    "input": {
      "customizations": {
        "main": {
          "section": {
            "cornerRadius": "LARGE",
            "colorScheme": "COLOR_SCHEME2",
            "shadow": "LARGE_200",
            "padding": "LARGE_400"
          }
        },
        "orderSummary": {
          "section": {
            "colorScheme": "COLOR_SCHEME1",
            "shadow": "LARGE_200",
            "padding": "LARGE_400",
            "border": "FULL"
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
  "query": "mutation ApplySectionStyles($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) { checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) { checkoutBranding { customizations { main { section { cornerRadius colorScheme shadow padding } } orderSummary { section { colorScheme shadow padding border } } } } userErrors { field message } } }",
   "variables": {
      "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
      "input": {
        "customizations": {
          "main": {
            "section": {
              "cornerRadius": "LARGE",
              "colorScheme": "COLOR_SCHEME2",
              "shadow": "LARGE_200",
              "padding": "LARGE_400"
            }
          },
          "orderSummary": {
            "section": {
              "colorScheme": "COLOR_SCHEME1",
              "shadow": "LARGE_200",
              "padding": "LARGE_400",
              "border": "FULL"
            }
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
    mutation ApplySectionStyles($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) {
      checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) {
        checkoutBranding {
          customizations {
            main {
              section {
                cornerRadius
                colorScheme
                shadow
                padding
              }
            }
            orderSummary {
              section {
                colorScheme
                shadow
                padding
                border
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
          "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
          "input": {
              "customizations": {
                  "main": {
                      "section": {
                          "cornerRadius": "LARGE",
                          "colorScheme": "COLOR_SCHEME2",
                          "shadow": "LARGE_200",
                          "padding": "LARGE_400"
                      }
                  },
                  "orderSummary": {
                      "section": {
                          "colorScheme": "COLOR_SCHEME1",
                          "shadow": "LARGE_200",
                          "padding": "LARGE_400",
                          "border": "FULL"
                      }
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
    mutation ApplySectionStyles($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) {
      checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) {
        checkoutBranding {
          customizations {
            main {
              section {
                cornerRadius
                colorScheme
                shadow
                padding
              }
            }
            orderSummary {
              section {
                colorScheme
                shadow
                padding
                border
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
    "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
    "input": {
      "customizations": {
        "main": {
          "section": {
            "cornerRadius": "LARGE",
            "colorScheme": "COLOR_SCHEME2",
            "shadow": "LARGE_200",
            "padding": "LARGE_400"
          }
        },
        "orderSummary": {
          "section": {
            "colorScheme": "COLOR_SCHEME1",
            "shadow": "LARGE_200",
            "padding": "LARGE_400",
            "border": "FULL"
          }
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
      "query": `mutation ApplySectionStyles($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) {
        checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) {
          checkoutBranding {
            customizations {
              main {
                section {
                  cornerRadius
                  colorScheme
                  shadow
                  padding
                }
              }
              orderSummary {
                section {
                  colorScheme
                  shadow
                  padding
                  border
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
          "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
          "input": {
              "customizations": {
                  "main": {
                      "section": {
                          "cornerRadius": "LARGE",
                          "colorScheme": "COLOR_SCHEME2",
                          "shadow": "LARGE_200",
                          "padding": "LARGE_400"
                      }
                  },
                  "orderSummary": {
                      "section": {
                          "colorScheme": "COLOR_SCHEME1",
                          "shadow": "LARGE_200",
                          "padding": "LARGE_400",
                          "border": "FULL"
                      }
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
  'mutation ApplySectionStyles($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) {
    checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) {
      checkoutBranding {
        customizations {
          main {
            section {
              cornerRadius
              colorScheme
              shadow
              padding
            }
          }
          orderSummary {
            section {
              colorScheme
              shadow
              padding
              border
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
    "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
    "input": {
      "customizations": {
        "main": {
          "section": {
            "cornerRadius": "LARGE",
            "colorScheme": "COLOR_SCHEME2",
            "shadow": "LARGE_200",
            "padding": "LARGE_400"
          }
        },
        "orderSummary": {
          "section": {
            "colorScheme": "COLOR_SCHEME1",
            "shadow": "LARGE_200",
            "padding": "LARGE_400",
            "border": "FULL"
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "checkoutBrandingUpsert": {
      "checkoutBranding": {
        "customizations": {
          "main": {
            "section": {
              "cornerRadius": "LARGE",
              "colorScheme": "COLOR_SCHEME2",
              "shadow": "LARGE_200",
              "padding": "LARGE_400"
            }
          },
          "orderSummary": {
            "section": {
              "colorScheme": "COLOR_SCHEME1",
              "shadow": "LARGE_200",
              "padding": "LARGE_400",
              "border": "FULL"
            }
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Modify a color scheme

  #### Query

  ```graphql
  mutation ChangeScheme2Colors($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) {
    checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) {
      checkoutBranding {
        designSystem {
          colors {
            schemes {
              scheme2 {
                base {
                  background
                  text
                }
              }
            }
          }
        }
      }
      userErrors {
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
    "input": {
      "designSystem": {
        "colors": {
          "schemes": {
            "scheme2": {
              "base": {
                "background": "#cdf7f3",
                "text": "#1f2928"
              }
            }
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
  "query": "mutation ChangeScheme2Colors($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) { checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) { checkoutBranding { designSystem { colors { schemes { scheme2 { base { background text } } } } } } userErrors { message } } }",
   "variables": {
      "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
      "input": {
        "designSystem": {
          "colors": {
            "schemes": {
              "scheme2": {
                "base": {
                  "background": "#cdf7f3",
                  "text": "#1f2928"
                }
              }
            }
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
    mutation ChangeScheme2Colors($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) {
      checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) {
        checkoutBranding {
          designSystem {
            colors {
              schemes {
                scheme2 {
                  base {
                    background
                    text
                  }
                }
              }
            }
          }
        }
        userErrors {
          message
        }
      }
    }`,
    {
      variables: {
          "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
          "input": {
              "designSystem": {
                  "colors": {
                      "schemes": {
                          "scheme2": {
                              "base": {
                                  "background": "#cdf7f3",
                                  "text": "#1f2928"
                              }
                          }
                      }
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
    mutation ChangeScheme2Colors($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) {
      checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) {
        checkoutBranding {
          designSystem {
            colors {
              schemes {
                scheme2 {
                  base {
                    background
                    text
                  }
                }
              }
            }
          }
        }
        userErrors {
          message
        }
      }
    }
  QUERY

  variables = {
    "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
    "input": {
      "designSystem": {
        "colors": {
          "schemes": {
            "scheme2": {
              "base": {
                "background": "#cdf7f3",
                "text": "#1f2928"
              }
            }
          }
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
      "query": `mutation ChangeScheme2Colors($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) {
        checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) {
          checkoutBranding {
            designSystem {
              colors {
                schemes {
                  scheme2 {
                    base {
                      background
                      text
                    }
                  }
                }
              }
            }
          }
          userErrors {
            message
          }
        }
      }`,
      "variables": {
          "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
          "input": {
              "designSystem": {
                  "colors": {
                      "schemes": {
                          "scheme2": {
                              "base": {
                                  "background": "#cdf7f3",
                                  "text": "#1f2928"
                              }
                          }
                      }
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
  'mutation ChangeScheme2Colors($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) {
    checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) {
      checkoutBranding {
        designSystem {
          colors {
            schemes {
              scheme2 {
                base {
                  background
                  text
                }
              }
            }
          }
        }
      }
      userErrors {
        message
      }
    }
  }' \
  --variables \
  '{
    "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
    "input": {
      "designSystem": {
        "colors": {
          "schemes": {
            "scheme2": {
              "base": {
                "background": "#cdf7f3",
                "text": "#1f2928"
              }
            }
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "checkoutBrandingUpsert": {
      "checkoutBranding": {
        "designSystem": {
          "colors": {
            "schemes": {
              "scheme2": {
                "base": {
                  "background": "#cdf7f3",
                  "text": "#1f2928"
                }
              }
            }
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Modify checkout font settings

  #### Query

  ```graphql
  mutation SetShopifyFonts($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) {
    checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) {
      checkoutBranding {
        designSystem {
          typography {
            size {
              base
              ratio
            }
            primary {
              name
              base {
                weight
              }
              bold {
                weight
              }
            }
            secondary {
              name
              base {
                weight
              }
              bold {
                weight
              }
            }
          }
        }
      }
      userErrors {
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
    "input": {
      "designSystem": {
        "typography": {
          "primary": {
            "shopifyFontGroup": {
              "name": "Univers Next"
            }
          },
          "secondary": {
            "shopifyFontGroup": {
              "name": "Univers Next"
            }
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
  "query": "mutation SetShopifyFonts($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) { checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) { checkoutBranding { designSystem { typography { size { base ratio } primary { name base { weight } bold { weight } } secondary { name base { weight } bold { weight } } } } } userErrors { message } } }",
   "variables": {
      "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
      "input": {
        "designSystem": {
          "typography": {
            "primary": {
              "shopifyFontGroup": {
                "name": "Univers Next"
              }
            },
            "secondary": {
              "shopifyFontGroup": {
                "name": "Univers Next"
              }
            }
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
    mutation SetShopifyFonts($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) {
      checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) {
        checkoutBranding {
          designSystem {
            typography {
              size {
                base
                ratio
              }
              primary {
                name
                base {
                  weight
                }
                bold {
                  weight
                }
              }
              secondary {
                name
                base {
                  weight
                }
                bold {
                  weight
                }
              }
            }
          }
        }
        userErrors {
          message
        }
      }
    }`,
    {
      variables: {
          "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
          "input": {
              "designSystem": {
                  "typography": {
                      "primary": {
                          "shopifyFontGroup": {
                              "name": "Univers Next"
                          }
                      },
                      "secondary": {
                          "shopifyFontGroup": {
                              "name": "Univers Next"
                          }
                      }
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
    mutation SetShopifyFonts($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) {
      checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) {
        checkoutBranding {
          designSystem {
            typography {
              size {
                base
                ratio
              }
              primary {
                name
                base {
                  weight
                }
                bold {
                  weight
                }
              }
              secondary {
                name
                base {
                  weight
                }
                bold {
                  weight
                }
              }
            }
          }
        }
        userErrors {
          message
        }
      }
    }
  QUERY

  variables = {
    "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
    "input": {
      "designSystem": {
        "typography": {
          "primary": {
            "shopifyFontGroup": {
              "name": "Univers Next"
            }
          },
          "secondary": {
            "shopifyFontGroup": {
              "name": "Univers Next"
            }
          }
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
      "query": `mutation SetShopifyFonts($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) {
        checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) {
          checkoutBranding {
            designSystem {
              typography {
                size {
                  base
                  ratio
                }
                primary {
                  name
                  base {
                    weight
                  }
                  bold {
                    weight
                  }
                }
                secondary {
                  name
                  base {
                    weight
                  }
                  bold {
                    weight
                  }
                }
              }
            }
          }
          userErrors {
            message
          }
        }
      }`,
      "variables": {
          "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
          "input": {
              "designSystem": {
                  "typography": {
                      "primary": {
                          "shopifyFontGroup": {
                              "name": "Univers Next"
                          }
                      },
                      "secondary": {
                          "shopifyFontGroup": {
                              "name": "Univers Next"
                          }
                      }
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
  'mutation SetShopifyFonts($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) {
    checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) {
      checkoutBranding {
        designSystem {
          typography {
            size {
              base
              ratio
            }
            primary {
              name
              base {
                weight
              }
              bold {
                weight
              }
            }
            secondary {
              name
              base {
                weight
              }
              bold {
                weight
              }
            }
          }
        }
      }
      userErrors {
        message
      }
    }
  }' \
  --variables \
  '{
    "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
    "input": {
      "designSystem": {
        "typography": {
          "primary": {
            "shopifyFontGroup": {
              "name": "Univers Next"
            }
          },
          "secondary": {
            "shopifyFontGroup": {
              "name": "Univers Next"
            }
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "checkoutBrandingUpsert": {
      "checkoutBranding": {
        "designSystem": {
          "typography": {
            "size": {
              "base": 14,
              "ratio": 1.2
            },
            "primary": {
              "name": "Univers Next",
              "base": {
                "weight": 400
              },
              "bold": {
                "weight": 700
              }
            },
            "secondary": {
              "name": "Univers Next",
              "base": {
                "weight": 400
              },
              "bold": {
                "weight": 700
              }
            }
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Modify global colors

  #### Query

  ```graphql
  mutation ChangeGlobalColors($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) {
    checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) {
      checkoutBranding {
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
      userErrors {
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
    "input": {
      "designSystem": {
        "colors": {
          "global": {
            "success": "#38e004",
            "warning": "#e0e004",
            "critical": "#e00404",
            "info": "#04e0e0",
            "brand": "#e004e0",
            "accent": "#04e004",
            "decorative": "#e0e0e0"
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
  "query": "mutation ChangeGlobalColors($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) { checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) { checkoutBranding { designSystem { colors { global { success warning critical info brand accent decorative } } } } userErrors { message } } }",
   "variables": {
      "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
      "input": {
        "designSystem": {
          "colors": {
            "global": {
              "success": "#38e004",
              "warning": "#e0e004",
              "critical": "#e00404",
              "info": "#04e0e0",
              "brand": "#e004e0",
              "accent": "#04e004",
              "decorative": "#e0e0e0"
            }
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
    mutation ChangeGlobalColors($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) {
      checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) {
        checkoutBranding {
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
        userErrors {
          message
        }
      }
    }`,
    {
      variables: {
          "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
          "input": {
              "designSystem": {
                  "colors": {
                      "global": {
                          "success": "#38e004",
                          "warning": "#e0e004",
                          "critical": "#e00404",
                          "info": "#04e0e0",
                          "brand": "#e004e0",
                          "accent": "#04e004",
                          "decorative": "#e0e0e0"
                      }
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
    mutation ChangeGlobalColors($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) {
      checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) {
        checkoutBranding {
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
        userErrors {
          message
        }
      }
    }
  QUERY

  variables = {
    "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
    "input": {
      "designSystem": {
        "colors": {
          "global": {
            "success": "#38e004",
            "warning": "#e0e004",
            "critical": "#e00404",
            "info": "#04e0e0",
            "brand": "#e004e0",
            "accent": "#04e004",
            "decorative": "#e0e0e0"
          }
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
      "query": `mutation ChangeGlobalColors($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) {
        checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) {
          checkoutBranding {
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
          userErrors {
            message
          }
        }
      }`,
      "variables": {
          "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
          "input": {
              "designSystem": {
                  "colors": {
                      "global": {
                          "success": "#38e004",
                          "warning": "#e0e004",
                          "critical": "#e00404",
                          "info": "#04e0e0",
                          "brand": "#e004e0",
                          "accent": "#04e004",
                          "decorative": "#e0e0e0"
                      }
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
  'mutation ChangeGlobalColors($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) {
    checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) {
      checkoutBranding {
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
      userErrors {
        message
      }
    }
  }' \
  --variables \
  '{
    "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
    "input": {
      "designSystem": {
        "colors": {
          "global": {
            "success": "#38e004",
            "warning": "#e0e004",
            "critical": "#e00404",
            "info": "#04e0e0",
            "brand": "#e004e0",
            "accent": "#04e004",
            "decorative": "#e0e0e0"
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "checkoutBrandingUpsert": {
      "checkoutBranding": {
        "designSystem": {
          "colors": {
            "global": {
              "success": "#38e004",
              "warning": "#e0e004",
              "critical": "#e00404",
              "info": "#04e0e0",
              "brand": "#e004e0",
              "accent": "#04e004",
              "decorative": "#e0e0e0"
            }
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Reset all styling to defaults

  #### Description

  Remove all checkout branding customizations and reset to the defaults.

  #### Query

  ```graphql
  mutation ChangeColorSchemeAndOrderSummary($checkoutBrandingInput: CheckoutBrandingInput, $checkoutProfileId: ID!) {
    checkoutBrandingUpsert(checkoutBrandingInput: $checkoutBrandingInput, checkoutProfileId: $checkoutProfileId) {
      checkoutBranding {
        designSystem {
          colors {
            schemes {
              scheme1 {
                base {
                  background
                  text
                }
              }
            }
          }
        }
        customizations {
          orderSummary {
            colorScheme
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
    "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
    "checkoutBrandingInput": null
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation ChangeColorSchemeAndOrderSummary($checkoutBrandingInput: CheckoutBrandingInput, $checkoutProfileId: ID!) { checkoutBrandingUpsert(checkoutBrandingInput: $checkoutBrandingInput, checkoutProfileId: $checkoutProfileId) { checkoutBranding { designSystem { colors { schemes { scheme1 { base { background text } } } } } customizations { orderSummary { colorScheme } } } userErrors { field message } } }",
   "variables": {
      "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
      "checkoutBrandingInput": null
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
    mutation ChangeColorSchemeAndOrderSummary($checkoutBrandingInput: CheckoutBrandingInput, $checkoutProfileId: ID!) {
      checkoutBrandingUpsert(checkoutBrandingInput: $checkoutBrandingInput, checkoutProfileId: $checkoutProfileId) {
        checkoutBranding {
          designSystem {
            colors {
              schemes {
                scheme1 {
                  base {
                    background
                    text
                  }
                }
              }
            }
          }
          customizations {
            orderSummary {
              colorScheme
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
          "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
          "checkoutBrandingInput": null
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
    mutation ChangeColorSchemeAndOrderSummary($checkoutBrandingInput: CheckoutBrandingInput, $checkoutProfileId: ID!) {
      checkoutBrandingUpsert(checkoutBrandingInput: $checkoutBrandingInput, checkoutProfileId: $checkoutProfileId) {
        checkoutBranding {
          designSystem {
            colors {
              schemes {
                scheme1 {
                  base {
                    background
                    text
                  }
                }
              }
            }
          }
          customizations {
            orderSummary {
              colorScheme
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
    "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
    "checkoutBrandingInput": null
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation ChangeColorSchemeAndOrderSummary($checkoutBrandingInput: CheckoutBrandingInput, $checkoutProfileId: ID!) {
        checkoutBrandingUpsert(checkoutBrandingInput: $checkoutBrandingInput, checkoutProfileId: $checkoutProfileId) {
          checkoutBranding {
            designSystem {
              colors {
                schemes {
                  scheme1 {
                    base {
                      background
                      text
                    }
                  }
                }
              }
            }
            customizations {
              orderSummary {
                colorScheme
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
          "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
          "checkoutBrandingInput": null
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation ChangeColorSchemeAndOrderSummary($checkoutBrandingInput: CheckoutBrandingInput, $checkoutProfileId: ID!) {
    checkoutBrandingUpsert(checkoutBrandingInput: $checkoutBrandingInput, checkoutProfileId: $checkoutProfileId) {
      checkoutBranding {
        designSystem {
          colors {
            schemes {
              scheme1 {
                base {
                  background
                  text
                }
              }
            }
          }
        }
        customizations {
          orderSummary {
            colorScheme
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
    "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
    "checkoutBrandingInput": null
  }'
  ```

  #### Response

  ```json
  {
    "checkoutBrandingUpsert": {
      "checkoutBranding": {
        "designSystem": null,
        "customizations": null
      },
      "userErrors": []
    }
  }
  ```

* ### Reset color schemes to the defaults

  #### Description

  Remove the customizations made to a color scheme and reset the scheme to the defaults.

  #### Query

  ```graphql
  mutation ChangeColorScheme1($checkoutBrandingInput: CheckoutBrandingInput!, $checkoutProfileId: ID!) {
    checkoutBrandingUpsert(checkoutBrandingInput: $checkoutBrandingInput, checkoutProfileId: $checkoutProfileId) {
      checkoutBranding {
        designSystem {
          colors {
            schemes {
              scheme1 {
                base {
                  background
                  text
                }
                control {
                  background
                  border
                  selected {
                    background
                    border
                  }
                }
                primaryButton {
                  hover {
                    background
                  }
                }
              }
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
    "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
    "checkoutBrandingInput": {
      "designSystem": {
        "colors": {
          "schemes": null
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
  "query": "mutation ChangeColorScheme1($checkoutBrandingInput: CheckoutBrandingInput!, $checkoutProfileId: ID!) { checkoutBrandingUpsert(checkoutBrandingInput: $checkoutBrandingInput, checkoutProfileId: $checkoutProfileId) { checkoutBranding { designSystem { colors { schemes { scheme1 { base { background text } control { background border selected { background border } } primaryButton { hover { background } } } } } } } userErrors { field message } } }",
   "variables": {
      "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
      "checkoutBrandingInput": {
        "designSystem": {
          "colors": {
            "schemes": null
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
    mutation ChangeColorScheme1($checkoutBrandingInput: CheckoutBrandingInput!, $checkoutProfileId: ID!) {
      checkoutBrandingUpsert(checkoutBrandingInput: $checkoutBrandingInput, checkoutProfileId: $checkoutProfileId) {
        checkoutBranding {
          designSystem {
            colors {
              schemes {
                scheme1 {
                  base {
                    background
                    text
                  }
                  control {
                    background
                    border
                    selected {
                      background
                      border
                    }
                  }
                  primaryButton {
                    hover {
                      background
                    }
                  }
                }
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
          "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
          "checkoutBrandingInput": {
              "designSystem": {
                  "colors": {
                      "schemes": null
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
    mutation ChangeColorScheme1($checkoutBrandingInput: CheckoutBrandingInput!, $checkoutProfileId: ID!) {
      checkoutBrandingUpsert(checkoutBrandingInput: $checkoutBrandingInput, checkoutProfileId: $checkoutProfileId) {
        checkoutBranding {
          designSystem {
            colors {
              schemes {
                scheme1 {
                  base {
                    background
                    text
                  }
                  control {
                    background
                    border
                    selected {
                      background
                      border
                    }
                  }
                  primaryButton {
                    hover {
                      background
                    }
                  }
                }
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
    "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
    "checkoutBrandingInput": {
      "designSystem": {
        "colors": {
          "schemes": null
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
      "query": `mutation ChangeColorScheme1($checkoutBrandingInput: CheckoutBrandingInput!, $checkoutProfileId: ID!) {
        checkoutBrandingUpsert(checkoutBrandingInput: $checkoutBrandingInput, checkoutProfileId: $checkoutProfileId) {
          checkoutBranding {
            designSystem {
              colors {
                schemes {
                  scheme1 {
                    base {
                      background
                      text
                    }
                    control {
                      background
                      border
                      selected {
                        background
                        border
                      }
                    }
                    primaryButton {
                      hover {
                        background
                      }
                    }
                  }
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
          "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
          "checkoutBrandingInput": {
              "designSystem": {
                  "colors": {
                      "schemes": null
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
  'mutation ChangeColorScheme1($checkoutBrandingInput: CheckoutBrandingInput!, $checkoutProfileId: ID!) {
    checkoutBrandingUpsert(checkoutBrandingInput: $checkoutBrandingInput, checkoutProfileId: $checkoutProfileId) {
      checkoutBranding {
        designSystem {
          colors {
            schemes {
              scheme1 {
                base {
                  background
                  text
                }
                control {
                  background
                  border
                  selected {
                    background
                    border
                  }
                }
                primaryButton {
                  hover {
                    background
                  }
                }
              }
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
    "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
    "checkoutBrandingInput": {
      "designSystem": {
        "colors": {
          "schemes": null
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "checkoutBrandingUpsert": {
      "checkoutBranding": {
        "designSystem": {
          "colors": {
            "schemes": null
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Set a checkout logo

  #### Description

  Modify the logo for checkout branding settings with a file already uploaded to Shopify (must not be of SVG format). Use the \[fileCreate]\(/api/admin-graphql/unstable/mutations/fileCreate) mutation to upload a new image to Shopify.

  #### Query

  ```graphql
  mutation SetLogo($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) {
    checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) {
      checkoutBranding {
        customizations {
          header {
            logo {
              image {
                url
              }
            }
          }
        }
      }
      userErrors {
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
    "input": {
      "customizations": {
        "header": {
          "logo": {
            "image": {
              "mediaImageId": null
            }
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
  "query": "mutation SetLogo($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) { checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) { checkoutBranding { customizations { header { logo { image { url } } } } } userErrors { message } } }",
   "variables": {
      "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
      "input": {
        "customizations": {
          "header": {
            "logo": {
              "image": {
                "mediaImageId": null
              }
            }
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
    mutation SetLogo($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) {
      checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) {
        checkoutBranding {
          customizations {
            header {
              logo {
                image {
                  url
                }
              }
            }
          }
        }
        userErrors {
          message
        }
      }
    }`,
    {
      variables: {
          "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
          "input": {
              "customizations": {
                  "header": {
                      "logo": {
                          "image": {
                              "mediaImageId": null
                          }
                      }
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
    mutation SetLogo($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) {
      checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) {
        checkoutBranding {
          customizations {
            header {
              logo {
                image {
                  url
                }
              }
            }
          }
        }
        userErrors {
          message
        }
      }
    }
  QUERY

  variables = {
    "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
    "input": {
      "customizations": {
        "header": {
          "logo": {
            "image": {
              "mediaImageId": null
            }
          }
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
      "query": `mutation SetLogo($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) {
        checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) {
          checkoutBranding {
            customizations {
              header {
                logo {
                  image {
                    url
                  }
                }
              }
            }
          }
          userErrors {
            message
          }
        }
      }`,
      "variables": {
          "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
          "input": {
              "customizations": {
                  "header": {
                      "logo": {
                          "image": {
                              "mediaImageId": null
                          }
                      }
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
  'mutation SetLogo($checkoutProfileId: ID!, $input: CheckoutBrandingInput!) {
    checkoutBrandingUpsert(checkoutProfileId: $checkoutProfileId, checkoutBrandingInput: $input) {
      checkoutBranding {
        customizations {
          header {
            logo {
              image {
                url
              }
            }
          }
        }
      }
      userErrors {
        message
      }
    }
  }' \
  --variables \
  '{
    "checkoutProfileId": "gid://shopify/CheckoutProfile/235093654",
    "input": {
      "customizations": {
        "header": {
          "logo": {
            "image": {
              "mediaImageId": null
            }
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "checkoutBrandingUpsert": {
      "checkoutBranding": {
        "customizations": {
          "header": {
            "logo": {
              "image": null
            }
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### checkoutBrandingUpsert reference
