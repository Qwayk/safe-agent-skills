from __future__ import annotations

import hashlib
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Any

import requests

from .oauth_tokens import read_token_json, token_path_for_env_file
from .redaction import redact_any
from .soap_actions_v13 import SOAP_ACTION_BY_SERVICE_AND_OPERATION
from .wsdl_namespaces_v13 import TARGET_NAMESPACE_BY_SERVICE


SOAP_ENV_NS = "http://schemas.xmlsoap.org/soap/envelope/"


def _utc(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))


def _soap_ns_tag(local: str) -> str:
    return f"{{{SOAP_ENV_NS}}}{local}"


def _append_dict_as_xml(parent: ET.Element, data: dict[str, Any]) -> None:
    for k, v in data.items():
        if v is None:
            continue
        child = ET.SubElement(parent, str(k))
        if isinstance(v, dict):
            _append_dict_as_xml(child, v)
        elif isinstance(v, list):
            # Represent lists as repeated child elements with the same key.
            # If a list contains dicts, nest them under each repeated element.
            parent.remove(child)
            for item in v:
                rep = ET.SubElement(parent, str(k))
                if isinstance(item, dict):
                    _append_dict_as_xml(rep, item)
                elif item is None:
                    continue
                else:
                    rep.text = str(item)
        else:
            child.text = str(v)


def build_soap_envelope(
    *,
    service: str,
    operation: str,
    auth: dict[str, str | None],
    request_obj: dict[str, Any],
) -> bytes:
    """
    Build a best-effort SOAP 1.1 request for Microsoft Ads v13.

    Important:
    - This is intentionally a minimal/portable XML builder (no heavy SOAP deps).
    - The request schema is provider-defined; complex nested payloads may require shaping `request_obj` accordingly.
    """
    tns = TARGET_NAMESPACE_BY_SERVICE[service]
    ET.register_namespace("soap", SOAP_ENV_NS)
    ET.register_namespace("tns", tns)

    env = ET.Element(_soap_ns_tag("Envelope"))
    header = ET.SubElement(env, _soap_ns_tag("Header"))
    body = ET.SubElement(env, _soap_ns_tag("Body"))

    def add_header(name: str, value: str | None) -> None:
        if value is None or not str(value).strip():
            return
        el = ET.SubElement(header, f"{{{tns}}}{name}")
        el.text = str(value)

    add_header("AuthenticationToken", auth.get("authentication_token"))
    add_header("DeveloperToken", auth.get("developer_token"))
    add_header("CustomerId", auth.get("customer_id"))
    add_header("CustomerAccountId", auth.get("customer_account_id"))

    op_el = ET.SubElement(body, f"{{{tns}}}{operation}")
    _append_dict_as_xml(op_el, request_obj)
    return ET.tostring(env, encoding="utf-8", xml_declaration=True)


@dataclass(frozen=True)
class SoapCallResult:
    ok: bool
    status: int | None
    url: str
    started_at_utc: str
    finished_at_utc: str
    response_text: str | None
    error: str | None


class MsAdsSoapClient:
    def __init__(
        self,
        *,
        env_file: str,
        timeout_s: float,
        verbose: bool,
        user_agent: str,
        endpoints: dict[str, str],
        developer_token: str | None,
        customer_id: str | None,
        customer_account_id: str | None,
    ) -> None:
        self._env_file = env_file
        self._timeout_s = timeout_s
        self._verbose = verbose
        self._user_agent = user_agent
        self._endpoints = endpoints
        self._developer_token = developer_token
        self._customer_id = customer_id
        self._customer_account_id = customer_account_id
        self._session = requests.Session()
        self._session.headers["User-Agent"] = user_agent

    def _access_token(self) -> str | None:
        tok_path = token_path_for_env_file(self._env_file)
        tok = read_token_json(tok_path) or {}
        v = tok.get("access_token")
        return str(v).strip() if isinstance(v, str) and v.strip() else None

    def build_plan(
        self,
        *,
        service: str,
        operation: str,
        request_obj: dict[str, Any],
        live: bool,
    ) -> dict[str, Any]:
        endpoint = self._endpoints[service]
        soap_action = SOAP_ACTION_BY_SERVICE_AND_OPERATION[service][operation]
        auth = {
            "developer_token_present": bool(self._developer_token),
            "customer_id_present": bool(self._customer_id),
            "customer_account_id_present": bool(self._customer_account_id),
            "access_token_present": bool(self._access_token()),
        }
        plan_id_src = f"{service}:{operation}:{endpoint}:{soap_action}"
        plan_id = hashlib.sha256(plan_id_src.encode("utf-8")).hexdigest()[:16]
        return {
            "plan_id": plan_id,
            "service": service,
            "operation": operation,
            "endpoint_url": endpoint,
            "soap_action": soap_action,
            "live": live,
            "auth": auth,
            "request": redact_any(request_obj),
        }

    def call(self, *, service: str, operation: str, request_obj: dict[str, Any]) -> SoapCallResult:
        endpoint = self._endpoints[service]
        soap_action = SOAP_ACTION_BY_SERVICE_AND_OPERATION[service][operation]

        started = time.time()
        started_utc = _utc(started)

        try:
            access_token = self._access_token()
            if not access_token:
                raise RuntimeError("Missing OAuth access_token (store token JSON via: msads-api-tool auth token set)")
            if not self._developer_token:
                raise RuntimeError("Missing MSADS_DEVELOPER_TOKEN in env file")

            envelope = build_soap_envelope(
                service=service,
                operation=operation,
                auth={
                    "authentication_token": access_token,
                    "developer_token": self._developer_token,
                    "customer_id": self._customer_id,
                    "customer_account_id": self._customer_account_id,
                },
                request_obj=request_obj,
            )

            headers = {
                "Content-Type": "text/xml; charset=utf-8",
                "SOAPAction": soap_action,
            }
            resp = self._session.post(
                endpoint,
                headers=headers,
                data=envelope,
                timeout=self._timeout_s,
            )
            finished = time.time()
            finished_utc = _utc(finished)
            # Avoid huge receipts: keep a bounded response string.
            text = resp.text
            if len(text) > 8000:
                text = text[:8000] + "\n... (truncated)\n"
            ok = resp.status_code < 400
            return SoapCallResult(
                ok=ok,
                status=resp.status_code,
                url=endpoint,
                started_at_utc=started_utc,
                finished_at_utc=finished_utc,
                response_text=text,
                error=None if ok else f"HTTP {resp.status_code}",
            )
        except Exception as e:  # noqa: BLE001
            finished = time.time()
            finished_utc = _utc(finished)
            return SoapCallResult(
                ok=False,
                status=None,
                url=endpoint,
                started_at_utc=started_utc,
                finished_at_utc=finished_utc,
                response_text=None,
                error=f"{type(e).__name__}: {e}",
            )

