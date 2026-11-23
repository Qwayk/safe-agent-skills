# Porkbun API sources

The tool ships [Porkbun's pinned v3.9 spec](../vendor/porkbun-openapi-v3.9.json). Its SHA-256 is `f4788709c27e0365e8a502180e0427bbcf7bd7558f3d7032bf34cf0a25dedd77`. The [coverage table](api_coverage.md) lists the 66 commands we ship from that version.

On November 23, 2026, we checked Porkbun's current v3.109 spec. It allows editing a DNS record by ID with only the fields you want to change. The tool uses that rule for `dns dns-edit`. The command to edit by name and type still requires `content`. The pinned inventory stays at v3.9.

- [Porkbun API documentation](https://porkbun.com/api/json/v3/documentation)
- [Current OpenAPI spec](https://porkbun.com/api/json/v3/spec)
- [Interactive docs and dry run details](https://porkbun.com/api/json/v3/documentation/interactive)
- [API key and domain setup](https://kb.porkbun.com/article/307-getting-started-porkbun-api)
- [Inventory generator](../scripts/generate_inventory.py)
