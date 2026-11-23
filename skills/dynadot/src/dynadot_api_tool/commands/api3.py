from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Type

from ._api3_specs import API3_PARAM_SPECS
from ._write_safety import WriteSpec, run_write_command
from ..dynadot_api import DynadotApi, DynadotApiError
from ..dynadot_api import is_write_command as _is_write_command
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import new_private_file, write_json_file


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _api(ctx: dict[str, Any]) -> DynadotApi:
    injected = ctx.get("api")
    if injected is not None:
        return injected  # type: ignore[return-value]
    cfg = ctx["cfg"]
    if not cfg.api_key:
        raise ValidationError("Missing DYNADOT_API_KEY")
    http = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx["verbose"]), user_agent="dynadot-api-tool")
    return DynadotApi(base_url=cfg.base_url, api_key=cfg.api_key, http=http)


def _require_api_key(ctx: dict[str, Any]) -> None:
    if not ctx["cfg"].api_key:
        raise ValidationError("Missing DYNADOT_API_KEY")


def _export_obj(ctx: dict[str, Any], *, command: str, params: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "dynadot-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": command,
        "params": params,
        "response": response,
    }


_NUM_SUFFIX_RE = re.compile(r"^(?P<base>[a-z_]+?)(?P<idx>\d+)$", re.IGNORECASE)


@dataclass(frozen=True)
class _ListKey:
    base: str
    required_count: int
    samples: list[str]


def _to_cli_name(command: str) -> str:
    return str(command).strip().lower().replace("_", "-")


def _to_flag_name(param: str) -> str:
    return str(param).strip().lower().replace("_", "-")


_IRREVERSIBLE = {
    "register",
    "bulk_register",
    "renew",
    "transfer",
    "delete",
    "buy_it_now",
    "buy_expired_closeout_domain",
    "place_auction_bid",
    "place_backorder_auction_bid",
    "add_backorder_request",
}


_NS_SUFFIX_RE = re.compile(r"^ns(?P<idx>\d+)$", re.IGNORECASE)


def _normalize_ns(value: object) -> str:
    s = str(value if value is not None else "").strip().lower()
    if s.endswith("."):
        s = s[:-1]
    return s


def _requested_ns_from_params(params: dict[str, Any]) -> list[str]:
    pairs: list[tuple[int, str]] = []
    for k, v in params.items():
        m = _NS_SUFFIX_RE.match(str(k or ""))
        if not m:
            continue
        s = _normalize_ns(v)
        if not s:
            continue
        pairs.append((int(m.group("idx")), s))
    return [s for _i, s in sorted(pairs)]


def _domains_from_param(value: object) -> list[str]:
    s = str(value if value is not None else "").strip()
    if not s:
        return []
    return [d.strip() for d in s.split(",") if d.strip()]


def _domains_from_params(params: dict[str, Any]) -> list[str]:
    # Most Dynadot API3 commands use `domain=...` (sometimes comma-separated), but a few use `domains=...`.
    domains: list[str] = []
    domains.extend(_domains_from_param(params.get("domain")))
    domains.extend(_domains_from_param(params.get("domains")))
    # Preserve order while de-duping.
    seen: set[str] = set()
    out: list[str] = []
    for d in domains:
        if d in seen:
            continue
        seen.add(d)
        out.append(d)
    return out


def _try_extract_order_id(obj: object) -> str | None:
    if not isinstance(obj, dict):
        return None
    for k in ("OrderId", "order_id", "orderId"):
        v = obj.get(k)
        if v is None:
            continue
        s = str(v).strip()
        if s:
            return s
    return None


def _safe_read_call(api: DynadotApi, *, command: str, params: dict[str, str] | None) -> dict[str, Any]:
    try:
        res = api.call(command=command, params=params)
        return {
            "ok": True,
            "command": command,
            "params": dict(params or {}),
            "dynadot": {"status": res.status, "response_code": res.response_code, "raw": res.response},
        }
    except Exception as e:  # noqa: BLE001
        return {
            "ok": False,
            "command": command,
            "params": dict(params or {}),
            "error": f"{type(e).__name__}: {e}",
        }


def _build_api3_verification(
    *,
    cmd: str,
    params: dict[str, Any],
    ctx: dict[str, Any],
) -> tuple[dict[str, Any], Callable[[], dict[str, Any]]]:
    """
    Best-effort verification for API3 writes.

    Standard goal: verify after write via read-back/idempotence. Dynadot’s API3 does not always expose a clean
    single-purpose "get_*" endpoint for every setting, so we use conservative, auditable snapshots.
    """
    c = str(cmd).strip().lower()
    domains = _domains_from_params(params)

    # Prefer command-specific read-backs when a clear read endpoint exists.
    if c in {"set_dns", "set_dns2"} and domains:
        verification_plan = {
            "type": "read-back-snapshot",
            "notes": "After apply, calls get_dns for each domain and records the response for review.",
            "commands": [{"command": "get_dns", "per_domain": True}],
            "domains": domains,
        }

        def _verify_dns() -> dict[str, Any]:
            _require_api_key(ctx)
            api = _api(ctx)
            results = [_safe_read_call(api, command="get_dns", params={"domain": d}) for d in domains]
            ok = all(bool(r.get("ok")) for r in results)
            return {"ok": ok, "type": "read-back-snapshot", "details": {"results": results}}

        return verification_plan, _verify_dns

    if c in {"create_contact", "edit_contact", "delete_contact"}:
        contact_id = str(params.get("contact_id") or "").strip() or None
        verification_plan = {
            "type": "read-back-snapshot",
            "notes": "After apply, snapshots contact_list (and get_contact when contact_id is known).",
            "commands": [{"command": "contact_list"}, {"command": "get_contact", "when": "contact_id present"}],
            "contact_id": contact_id,
        }

        def _verify_contacts() -> dict[str, Any]:
            _require_api_key(ctx)
            api = _api(ctx)
            results: list[dict[str, Any]] = []
            results.append(_safe_read_call(api, command="contact_list", params=None))
            if contact_id:
                results.append(_safe_read_call(api, command="get_contact", params={"contact_id": contact_id}))
            ok = all(bool(r.get("ok")) for r in results)
            return {"ok": ok, "type": "read-back-snapshot", "details": {"results": results}}

        return verification_plan, _verify_contacts

    if c in {"create_folder", "delete_folder", "set_folder_name"} or c.startswith("set_folder_"):
        folder_id = str(params.get("folder_id") or "").strip() or None
        verification_plan = {
            "type": "read-back-snapshot",
            "notes": "After apply, snapshots folder_list for review.",
            "commands": [{"command": "folder_list"}],
            "folder_id": folder_id,
        }

        def _verify_folders() -> dict[str, Any]:
            _require_api_key(ctx)
            api = _api(ctx)
            results = [_safe_read_call(api, command="folder_list", params=None)]
            ok = all(bool(r.get("ok")) for r in results)
            return {"ok": ok, "type": "read-back-snapshot", "details": {"results": results}}

        return verification_plan, _verify_folders

    if c in {"add_ns", "delete_ns", "delete_ns_by_domain", "register_ns", "set_ns_ip"}:
        verification_plan = {
            "type": "read-back-snapshot",
            "notes": "After apply, snapshots server_list for review.",
            "commands": [{"command": "server_list"}],
        }

        def _verify_servers() -> dict[str, Any]:
            _require_api_key(ctx)
            api = _api(ctx)
            results = [_safe_read_call(api, command="server_list", params=None)]
            ok = all(bool(r.get("ok")) for r in results)
            return {"ok": ok, "type": "read-back-snapshot", "details": {"results": results}}

        return verification_plan, _verify_servers

    # Generic domain snapshot for domain-targeting writes.
    if domains:
        verification_plan = {
            "type": "read-back-snapshot",
            "notes": "After apply, calls domain_info for each domain and records the response for review.",
            "commands": [{"command": "domain_info", "per_domain": True}],
            "domains": domains,
        }

        def _verify_domains() -> dict[str, Any]:
            _require_api_key(ctx)
            api = _api(ctx)
            results = [_safe_read_call(api, command="domain_info", params={"domain": d}) for d in domains]
            ok = all(bool(r.get("ok")) for r in results)
            return {"ok": ok, "type": "read-back-snapshot", "details": {"results": results}}

        return verification_plan, _verify_domains

    # Account-level defaults / misc: snapshot account_info.
    verification_plan = {
        "type": "read-back-snapshot",
        "notes": "After apply, snapshots account_info for review.",
        "commands": [{"command": "account_info"}],
    }

    def _verify_account() -> dict[str, Any]:
        _require_api_key(ctx)
        api = _api(ctx)
        results = [_safe_read_call(api, command="account_info", params=None)]
        ok = all(bool(r.get("ok")) for r in results)
        return {"ok": ok, "type": "read-back-snapshot", "details": {"results": results}}

    return verification_plan, _verify_account


def _get_ns_hosts(resp: dict[str, Any]) -> list[str]:
    ns_content = resp.get("NsContent")
    if isinstance(ns_content, dict):
        host_obj = ns_content
    else:
        host_obj = None

    out: list[str] = []
    for i in range(0, 13):
        v = None
        if host_obj is not None:
            v = host_obj.get(f"Host{i}")
        if v is None:
            v = resp.get(f"Host{i}")
        ns = _normalize_ns(v)
        if ns:
            out.append(ns)
    return out


def _selector_value_from_params(params: dict[str, Any]) -> str | None:
    for k in ("domain", "domain_name", "domains", "folder_name", "folder_id", "contact_id", "order_id"):
        v = params.get(k)
        if v is None:
            continue
        s = str(v).strip()
        if s:
            return s
    return None


def _collect_param_shapes(command: str) -> tuple[list[dict[str, object]], dict[str, _ListKey], list[str]]:
    specs = API3_PARAM_SPECS.get(command, [])
    scalar_params: list[dict[str, object]] = []
    list_params: dict[str, _ListKey] = {}
    unknown: list[str] = []

    numeric_bases: dict[str, set[int]] = {}
    for row in specs:
        name_any = row.get("name")
        if not isinstance(name_any, str):
            continue
        name = name_any.strip()
        if not name:
            continue
        m = _NUM_SUFFIX_RE.match(name)
        if not m:
            continue
        base = m.group("base").lower()
        idx = int(m.group("idx"))
        numeric_bases.setdefault(base, set()).add(idx)

    list_bases = {b for b, idxs in numeric_bases.items() if 0 in idxs}

    for row in specs:
        name_any = row.get("name")
        if not isinstance(name_any, str):
            unknown.append(str(name_any))
            continue
        name = name_any.strip()
        if not name:
            continue
        m = _NUM_SUFFIX_RE.match(name)
        if m and m.group("base").lower() in list_bases:
            base = m.group("base").lower()
            idx = int(m.group("idx"))
            required = bool(row.get("required"))
            sample = row.get("sample")
            s = str(sample) if sample is not None else ""
            prev = list_params.get(base)
            required_count = max((prev.required_count if prev else 0), (idx + 1 if required else 0))
            samples = list(prev.samples) if prev else []
            if len(samples) <= idx:
                samples.extend([""] * (idx + 1 - len(samples)))
            samples[idx] = s
            list_params[base] = _ListKey(base=base, required_count=required_count, samples=samples)
            continue
        scalar_params.append(row)

    return (scalar_params, list_params, unknown)


def _parse_scalar_params(args: Any, scalar_rows: list[dict[str, object]]) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for row in scalar_rows:
        name_any = row.get("name")
        if not isinstance(name_any, str):
            continue
        name = name_any.strip()
        if not name:
            continue
        attr = name.lower()
        v = getattr(args, attr, None)
        if v is None:
            continue
        s = str(v).strip()
        if s == "":
            continue
        params[name] = s
    return params


def _parse_list_params(args: Any, list_params: dict[str, _ListKey]) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for base, lk in sorted(list_params.items()):
        values: list[str] = []
        raw_list = getattr(args, base.lower(), None)
        if isinstance(raw_list, list):
            for item in raw_list:
                s = str(item or "").strip()
                if s:
                    values.append(s)
        if lk.required_count and len(values) < lk.required_count:
            raise ValidationError(f"--{_to_flag_name(base)} requires at least {lk.required_count} value(s)")
        for i, v in enumerate(values):
            params[f"{base}{i}"] = v
    return params


def _add_scalar_args(p: argparse.ArgumentParser, scalar_rows: list[dict[str, object]]) -> None:
    for row in scalar_rows:
        name_any = row.get("name")
        if not isinstance(name_any, str):
            continue
        name = name_any.strip()
        if not name:
            continue
        required = bool(row.get("required"))
        flag = f"--{_to_flag_name(name)}"
        dest = name.lower()
        p.add_argument(flag, dest=dest, required=required, default=None, help=f"Dynadot API param: {name}")


def _add_list_args(p: argparse.ArgumentParser, list_params: dict[str, _ListKey]) -> None:
    for base, lk in sorted(list_params.items()):
        flag = f"--{_to_flag_name(base)}"
        p.add_argument(flag, dest=base.lower(), action="append", default=None, help=f"Dynadot API params: {base}0..")


_QUOTED_COMMANDS = {"register", "renew"}
_PRICE_VALUE = re.compile(
    r"(?:Registration Price:\s*)?(\d+(?:\.\d+)?)\s*(?:in\s+)?([A-Z]{3})?"
    r"(?: and Domain is (?:not )?a Premium Domain)?",
    re.IGNORECASE,
)


def _price(value: Any, currency: str = "") -> tuple[Decimal, str] | None:
    if isinstance(value, dict):
        currency = str(value.get("Currency") or currency)
        value = value.get("TotalPrice", value.get("Price"))
    match = _PRICE_VALUE.fullmatch(str(value if value is not None else "").strip())
    if not match:
        return None
    return Decimal(match[1]), (match[2] or currency).upper()


def _purchase_quote(cmd: str, params: dict[str, Any], ctx: dict[str, Any]) -> dict[str, str]:
    currency = str(params.get("currency") or "").upper()
    if not re.fullmatch("[A-Z]{3}", currency):
        return {"status": "unavailable", "reason": "Choose a currency to check the price."}
    if not ctx["cfg"].api_key:
        return {"status": "unavailable", "reason": "Set your Dynadot key to check the price."}
    if cmd == "register" and str(params.get("duration")) != "1":
        return {"status": "unavailable", "reason": "The API3 search price is for one year. Check the full term at Dynadot checkout."}

    try:
        api = _api(ctx)
        if cmd == "renew":
            response = api.call(command="renew", params=params | {"price_check": "1"}).response
            value = response.get("PriceInfo") if str(response.get("Status")).lower() == "price_check_success" else None
        else:
            domain = str(params["domain"]).lower().rstrip(".")
            response = api.call(
                command="search", params={"domain0": domain, "show_price": "1", "currency": currency}
            ).response
            rows = response.get("SearchResults")
            matches = [
                row for row in rows
                if isinstance(row, dict)
                and str(row.get("DomainName", "")).lower().rstrip(".") == domain
                and str(row.get("Available", "")).lower() == "yes"
                and str(row.get("Status") or "success").lower() == "success"
            ] if isinstance(rows, list) else []
            value = matches[0].get("Price") if len(matches) == 1 else None
    except (RuntimeError, ValidationError, DynadotApiError):
        value = None
    quote = _price(value, str(response.get("Currency") or "") if value is not None else "")
    if quote is None or quote[1] != currency:
        return {"status": "unavailable", "reason": "Dynadot did not return a price in the selected currency."}
    return {"status": "quoted", "amount": str(quote[0]), "currency": quote[1]}


def _checked_purchase_quote(
    cmd: str, params: dict[str, Any], ctx: dict[str, Any], plan: dict[str, Any]
) -> dict[str, str]:
    maximum = (plan.get("baseline") or {}).get("max_price")
    reviewed_quote = (plan.get("preview") or {}).get("quote") or {}
    if maximum is None or reviewed_quote.get("status") != "quoted":
        raise SafetyError("Save a new plan with a Dynadot quote and the approved --max-price.")
    if Decimal(reviewed_quote["amount"]) > Decimal(maximum):
        raise SafetyError("The reviewed quote was above the approved maximum. Save and review a new plan.")
    fresh_quote = _purchase_quote(cmd, params, ctx)
    if fresh_quote["status"] != "quoted":
        raise SafetyError("Dynadot did not confirm the current price. Check it before creating an order.")
    if Decimal(fresh_quote["amount"]) > Decimal(maximum):
        raise SafetyError("Dynadot's current quote is above the approved maximum. No order was sent.")
    return fresh_quote


def cmd_api3_call(args: Any, ctx: dict[str, Any]) -> int:
    cmd = str(getattr(args, "api3_command", "") or "").strip().lower().replace("-", "_")
    if not cmd:
        raise ValidationError("Missing api3 command")

    scalar_rows, list_params, _unknown = _collect_param_shapes(cmd)
    params: dict[str, Any] = {}
    params.update(_parse_scalar_params(args, scalar_rows))
    params.update(_parse_list_params(args, list_params))

    if not _is_write_command(cmd):
        _require_api_key(ctx)
        api = _api(ctx)
        res = api.call(command=cmd, params=params)
        out_path = str(getattr(args, "out", "") or "").strip() or None
        export_written = (
            write_json_file(out_path, _export_obj(ctx, command=cmd, params=dict(params), response=res.response))
            if out_path
            else None
        )
        out = {
            "ok": True,
            "dry_run": True,
            "command": cmd,
            "params": params,
            "out_path": export_written,
            "dynadot": {"command": cmd, "status": res.status, "response_code": res.response_code, "raw": res.response},
        }
        ctx["audit"].write(f"api3.{cmd}.read", {"out_path": export_written})
        ctx["out"].emit(out)
        return 0

    irreversible = cmd in _IRREVERSIBLE
    selector_kind = f"api3.{cmd}"
    selector_value = _selector_value_from_params(params)
    risk_level = "irreversible" if irreversible else "high"
    risk_reasons = ["dynadot-api3-write"] + (["irreversible/monetary"] if irreversible else [])

    verify_call = None
    verification_plan: dict[str, Any] = {
        "type": "api-response-only",
        "notes": "Best-effort: verify ResponseCode=0 from Dynadot.",
    }
    if cmd == "set_ns":
        requested = _requested_ns_from_params(params)
        domains = _domains_from_param(params.get("domain"))
        verification_plan = {
            "type": "read-back",
            "notes": "After apply, calls get_ns for each domain and compares returned NsContent.Host* to requested ns* params.",
            "domains": domains,
            "requested_nameservers": requested,
        }

        def _verify_set_ns() -> dict[str, Any]:
            _require_api_key(ctx)
            api = _api(ctx)
            results: list[dict[str, Any]] = []
            ok = True

            if not domains:
                return {"ok": False, "type": "read-back", "details": {"error": "Missing domain param for set_ns verification"}}
            if not requested:
                return {"ok": False, "type": "read-back", "details": {"error": "Missing ns* params for set_ns verification"}}

            for domain in domains:
                res = api.call(command="get_ns", params={"domain": domain})
                actual = _get_ns_hosts(res.response)
                match = actual == requested
                ok = ok and match
                results.append(
                    {
                        "domain": domain,
                        "requested": requested,
                        "actual": actual,
                        "match": match,
                        "dynadot": {"status": res.status, "response_code": res.response_code},
                    }
                )
            return {"ok": ok, "type": "read-back", "details": {"results": results}}

        verify_call = _verify_set_ns

    if verify_call is None:
        verification_plan, verify_call = _build_api3_verification(cmd=cmd, params=params, ctx=ctx)

    public_params = dict(params)
    protected_params = dict(params)
    for name in ("auth", "auth_code"):
        if name in params:
            public_params[name] = "[private]"
            credential = str(ctx["cfg"].api_key or "").encode()
            protected_params[name] = hmac.new(
                credential, ("dynadot-private-input:" + str(params[name])).encode(), hashlib.sha256
            ).hexdigest() if credential else None

    baseline: dict[str, Any] = {"params": protected_params}
    preview: dict[str, Any] = {"params": public_params}
    if cmd in _QUOTED_COMMANDS:
        limit = getattr(args, "max_price", None)
        if limit is not None and not re.fullmatch(r"[0-9]+(?:\.[0-9]{1,2})?", limit):
            raise ValidationError("--max-price must be a nonnegative amount, such as 15.00.")
        baseline["max_price"] = str(Decimal(limit)) if limit is not None else None
        preview["max_price"] = baseline["max_price"]
        if not ctx.get("apply") and not ctx.get("plan_in"):
            preview["quote"] = _purchase_quote(cmd, params, ctx)
            preview["price_note"] = "The tool checks the quote again before sending an order. Dynadot sets the final charge."

    spec = WriteSpec(
        api_command=cmd,
        selector_kind=selector_kind,
        selector_value=selector_value,
        risk_level=risk_level,
        risk_reasons=risk_reasons,
        irreversible=irreversible,
        baseline=baseline,
        preview=preview,
        proposed_changes=[{"params": public_params}],
        verification_plan=verification_plan,
        rollback={"supported": False, "notes": "Most Dynadot writes are not safely auto-reversible."},
    )

    def _apply_call(plan: dict[str, Any]) -> dict[str, Any]:
        _require_api_key(ctx)
        quote = _checked_purchase_quote(cmd, params, ctx, plan) if cmd in _QUOTED_COMMANDS else None
        api = _api(ctx)
        if cmd == "get_transfer_auth_code":
            secret_out = str(getattr(args, "secret_out", None) or "").strip()
            if not secret_out:
                raise ValidationError("Use --secret-out with a new private file for the transfer code.")
            with new_private_file(secret_out) as secret_file:
                result = api.call(command=cmd, params=params)
                json.dump(result.response, secret_file, ensure_ascii=False, indent=2)
                secret_file.write("\n")
            return {"ok": True, "status": result.status, "response_code": result.response_code, "secret_out": secret_out}

        res = api.call(command=cmd, params=params)
        out = {"ok": True, "status": res.status, "response_code": res.response_code, "raw": res.response}
        if quote is not None:
            out["quote_before_request"] = quote
        oid = _try_extract_order_id(res.response)
        if oid:
            out["order_id"] = oid
        return out

    return run_write_command(ctx=ctx, spec=spec, apply_call=_apply_call, verify_call=verify_call)


def register_api3(
    subparsers: argparse._SubParsersAction,  # type: ignore[name-defined]
    *,
    parser_class: Type[argparse.ArgumentParser],
) -> None:
    api3 = subparsers.add_parser("api3", help="Named commands for the pinned Dynadot API3 list")
    api3_sub = api3.add_subparsers(dest="api3_cmd", required=True, parser_class=parser_class)

    for cmd in sorted(API3_PARAM_SPECS.keys()):
        cli_name = _to_cli_name(cmd)
        p = api3_sub.add_parser(cli_name, help=f"Dynadot API3 command: {cmd}")
        p.set_defaults(func=cmd_api3_call, write_capable=_is_write_command(cmd), api3_command=cmd)

        scalar_rows, list_params, _unknown = _collect_param_shapes(cmd)
        _add_scalar_args(p, scalar_rows)
        _add_list_args(p, list_params)

        if cmd in _QUOTED_COMMANDS:
            p.add_argument("--max-price", help="Approved total in the selected currency")
        if cmd == "get_transfer_auth_code":
            p.add_argument("--secret-out", help="Save the code in a new private file during apply")
        if not _is_write_command(cmd):
            p.add_argument("--out", default=None, help="Write full JSON export to a file")
