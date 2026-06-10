from __future__ import annotations


def cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]

    product: dict[str, object] = {
        "configured_context": cfg.has_product_context(),
        "configured_credentials": cfg.has_product_basic_auth(),
        "host": cfg.product_api_host,
        "cloud_name": cfg.cloud_name,
    }
    account: dict[str, object] = {
        "configured_context": cfg.has_account_context(),
        "configured_credentials": cfg.has_account_basic_auth(),
        "host": cfg.account_api_host,
        "account_id": cfg.account_id,
    }

    if cfg.has_product_basic_auth():
        try:
            response = ctx["http"].request(
                "GET",
                cfg.product_v1_base_url() + "/ping",
                headers=cfg.product_auth_header(),
            )
            product["ready"] = True
            product["http_status"] = response.status
        except Exception as exc:  # noqa: BLE001
            product["ready"] = False
            product["error"] = cfg.redact(str(exc))
    else:
        missing: list[str] = []
        if not cfg.cloud_name:
            missing.append("CLOUDINARY_CLOUD_NAME")
        if not cfg.api_key:
            missing.append("CLOUDINARY_API_KEY")
        if not cfg.api_secret:
            missing.append("CLOUDINARY_API_SECRET")
        product["ready"] = False
        product["setup_required"] = missing

    if cfg.has_account_basic_auth():
        try:
            response = ctx["http"].request_allow_error(
                "GET",
                cfg.account_provisioning_base_url() + "/sub_accounts",
                headers=cfg.account_auth_header(),
            )
            account["ready"] = response.status < 400
            account["http_status"] = response.status
            if response.status >= 400:
                account["error"] = cfg.redact(response.text())
        except Exception as exc:  # noqa: BLE001
            account["ready"] = False
            account["error"] = cfg.redact(str(exc))
    else:
        missing = []
        if not cfg.account_id:
            missing.append("CLOUDINARY_ACCOUNT_ID")
        if not cfg.account_api_key:
            missing.append("CLOUDINARY_ACCOUNT_API_KEY")
        if not cfg.account_api_secret:
            missing.append("CLOUDINARY_ACCOUNT_API_SECRET")
        account["ready"] = False
        account["setup_required"] = missing

    payload = {
        "ok": True,
        "env_fingerprint": cfg.env_fingerprint(),
        "checks": {
            "product": product,
            "account": account,
            "permissions_public": {
                "ready": True,
                "notes": "Permissions public catalog/schema/validate endpoints do not require credentials.",
            },
        },
    }
    ctx["audit"].write("auth.check", payload)
    ctx["out"].emit(payload)
    return 0
