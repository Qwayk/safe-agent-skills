# Batch endpoints

WooCommerce ships many official `POST /.../batch` endpoints.
This tool exposes them as explicit `batch` actions under each family.

Examples:

- `coupons batch`
- `customers batch`
- `orders batch`
- `products batch`
- `product-variations batch`
- `taxes batch`
- `webhooks batch`

Batch calls are high-risk writes.
Use the normal safety flow:

1. dry-run first
2. review the plan
3. request apply with `--apply --plan-in`
4. add `--yes` because batch writes are high-risk

Current batch apply requests require explicit no-snapshot approval before WooCommerce HTTP until the operation can save real before-state when possible.
