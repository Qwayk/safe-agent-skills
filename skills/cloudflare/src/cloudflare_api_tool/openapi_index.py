from __future__ import annotations
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import ToolError


@dataclass(frozen=True)
class OperationSpec:
    area: str
    method: str
    path_template: str
    operation_id: str | None
    summary: str
    tags: str
    deprecated: bool
    api_token_groups: str
    sensitivity: str  # "none" | "sensitive_read" | "sensitive_write_result"


def _tool_root() -> Path:
    # .../api-tools/<tool>/src/cloudflare_api_tool/openapi_index.py -> tool root is parents[2]
    return Path(__file__).resolve().parents[2]


_ACCOUNT_SCOPED_PATH_RE = re.compile(r"^/accounts/\{[^}]+\}(?:/|$)")


def _account_scoped_rest(path: str) -> str | None:
    """
    Returns the portion of an account-scoped path template after `/accounts/{...}/`, or `""` for `/accounts/{...}`.

    Cloudflare's OpenAPI snapshot uses multiple placeholder names for account IDs (example: `{account_id}`,
    `{accountId}`, `{account_identifier}`); this helper keeps sensitivity rules correct across variants.
    """
    p = str(path or "").strip()
    m = _ACCOUNT_SCOPED_PATH_RE.match(p)
    if not m:
        return None
    return p[m.end() :]


def is_read_like_non_get_operation(spec: OperationSpec | None) -> bool:
    """
    Some Cloudflare APIs use non-GET methods for read-like operations (example: preview/validate/trace).

    These operations are treated as:
    - non-mutating for gating/receipts (do not require --yes; receipts report changed=false)
    - still plan-first unless `--apply` is provided

    Note: sensitivity (file-only output; never printed) is governed by `OperationSpec.sensitivity`
    and enforced by the allowlisted operations runner, not by this helper.
    """
    if spec is None:
        return False
    if str(spec.method or "").upper().strip() == "GET":
        return False
    # Phase 14: Workers AI model runs are read-like POSTs (no state changes expected).
    if str(spec.method or "").upper().strip() == "POST":
        rest = _account_scoped_rest(str(spec.path_template or "").strip())
        if rest is not None and rest.startswith("ai/run/"):
            return True
    op_id = str(spec.operation_id or "").strip()
    if op_id in {
        "workers-kv-namespace-get-multiple-key-value-pairs",
        "queues-pull-messages",
        # Cloudflare renamed some D1 operationIds in the upstream OpenAPI snapshot (kept for compatibility).
        "cloudflare-d1-export-database",
        "d1-export-database",
        "postV4AccountsByAccount_idPipelinesV1Validate_sql",
        # Workers Observability Telemetry: read-like POSTs (query/keys/values).
        "telemetry.query",
        "telemetry.keys.list",
        "telemetry.values.list",
        # Request Tracer: read-like trace operation is a POST.
        "account-request-tracer-request-trace",
        # Load Balancing: preview endpoints are read-like POSTs.
        "account-load-balancer-monitors-preview-monitor",
        "account-load-balancer-pools-preview-pool",
        # Waiting Room: preview endpoint is a read-like POST.
        "waiting-room-create-a-custom-waiting-room-page-preview",
        # Phase 10: Images direct upload URL is a read-like POST (returns an upload URL; no state mutation expected).
        "cloudflare-images-create-authenticated-direct-upload-url-v-2",
        # Phase 12: Vectorize v2 read-like POSTs (query/get-by-ids).
        "vectorize-query-vector",
        "vectorize-get-vectors-by-id",
        # Phase 13: AutoRAG read-like POSTs (RAG search; no state changes expected).
        "autorag-config-ai-search",
        "autorag-config-search",
        # Phase 15: AI Search read-like POSTs (search/chat; no state changes expected).
        "ai-search-instance-search",
        "ai-search-instance-chat-completion",
        # Browser Rendering and Workers Tail start return output/session details without changing account config.
        "worker-tail-logs-start-tail",
    }:
        return True
    path_template = str(spec.path_template or "").strip()
    if str(spec.method or "").upper().strip() == "POST" and path_template.startswith("/accounts/{account_id}/browser-rendering/"):
        return True
    # Fallback: match deterministic method+path when operationId is absent.
    if (str(spec.method or "").upper().strip(), path_template) in {
        ("POST", "/accounts/{account_id}/storage/kv/namespaces/{namespace_id}/bulk/get"),
        ("POST", "/accounts/{account_id}/queues/{queue_id}/messages/pull"),
        ("POST", "/accounts/{account_id}/d1/database/{database_id}/export"),
        ("POST", "/accounts/{account_id}/pipelines/v1/validate_sql"),
        ("POST", "/telemetry/query"),
        ("POST", "/telemetry/keys"),
        ("POST", "/telemetry/values"),
        ("POST", "/accounts/{account_id}/request-tracer/trace"),
        ("POST", "/zones/{zone_id}/ssl/analyze"),
        ("POST", "/accounts/{account_id}/load_balancers/monitors/{monitor_id}/preview"),
        ("POST", "/accounts/{account_id}/load_balancers/pools/{pool_id}/preview"),
        ("POST", "/zones/{zone_id}/waiting_rooms/preview"),
        ("POST", "/accounts/{account_id}/images/v2/direct_upload"),
        ("POST", "/accounts/{account_id}/vectorize/v2/indexes/{index_name}/query"),
        ("POST", "/accounts/{account_id}/vectorize/v2/indexes/{index_name}/get_by_ids"),
        ("POST", "/accounts/{account_id}/autorag/rags/{id}/ai-search"),
        ("POST", "/accounts/{account_id}/autorag/rags/{id}/search"),
        ("POST", "/accounts/{account_id}/ai-search/namespaces/{name}/chat/completions"),
        ("POST", "/accounts/{account_id}/ai-search/namespaces/{name}/search"),
        ("POST", "/accounts/{account_id}/ai-search/instances/{id}/search"),
        ("POST", "/accounts/{account_id}/ai-search/instances/{id}/chat/completions"),
        ("POST", "/accounts/{account_id}/ai-search/namespaces/{name}/instances/{id}/chat/completions"),
        ("POST", "/accounts/{account_id}/ai-search/namespaces/{name}/instances/{id}/search"),
        ("POST", "/accounts/{account_id}/workers/scripts/{script_name}/tails"),
    }:
        return True
    return False


def _is_sensitive_read(*, method: str, path: str, summary: str, operation_id: str, api_token_groups: str) -> bool:
    if method != "GET":
        return False
    hay = " ".join([path, summary, operation_id]).lower()
    if "pii" in str(api_token_groups or "").lower():
        return True
    # Cloudflare uses "User Details" token groups for endpoints that can reveal user-identifying data.
    if "user details" in str(api_token_groups or "").lower():
        return True
    if "/content" in hay:
        return True
    if "/values" in hay:
        return True
    if "/token" in hay or " token" in hay:
        return True
    # Workers download endpoints can be code.
    rest = _account_scoped_rest(path)
    if rest == "workers/scripts/{script_name}":
        return True
    if path.startswith("/telemetry/"):
        return True
    return False


def _is_sensitive_write_result(*, method: str, path: str, summary: str, operation_id: str, api_token_groups: str) -> bool:
    if method == "GET":
        return False
    hay = " ".join([path, summary, operation_id]).lower()
    if "pii" in str(api_token_groups or "").lower():
        return True
    if "user details" in str(api_token_groups or "").lower():
        return True
    # Some endpoints return temporary upload/auth tokens (example: assets upload sessions return a JWT).
    if "assets-upload-session" in hay or " jwt" in hay or hay.startswith("jwt "):
        return True
    if "/token" in hay or " token" in hay:
        return True
    if "service token" in hay:
        return True
    if "client_secret" in hay or "client secret" in hay:
        return True
    return False


class OperationIndex:
    def __init__(self, *, specs: list[OperationSpec]) -> None:
        self._specs = list(specs)
        self._by_op_id: dict[str, OperationSpec] = {}
        self._by_method_path: dict[tuple[str, str], OperationSpec] = {}
        for s in self._specs:
            if s.operation_id:
                self._by_op_id[s.operation_id] = s
            self._by_method_path[(s.method, s.path_template)] = s

    def get(self, operation_id: str) -> OperationSpec | None:
        return self._by_op_id.get(str(operation_id or "").strip())

    def get_by_method_path(self, *, method: str, path_template: str) -> OperationSpec | None:
        return self._by_method_path.get((str(method or "").upper().strip(), str(path_template or "").strip()))

    def all_specs(self) -> list[OperationSpec]:
        return list(self._specs)

    def find(
        self,
        *,
        contains: str | None = None,
        tag: str | None = None,
        method: str | None = None,
        include_deprecated: bool = False,
        include_sensitive: bool = False,
        limit: int = 200,
    ) -> list[OperationSpec]:
        needle = str(contains or "").strip().lower()
        tag_needle = str(tag or "").strip().lower()
        method_needle = str(method or "").strip().upper()

        out: list[OperationSpec] = []
        for s in self._specs:
            if not include_deprecated and s.deprecated:
                continue
            if not include_sensitive and s.sensitivity != "none":
                continue
            if method_needle and s.method != method_needle:
                continue
            if tag_needle and tag_needle not in str(s.tags or "").lower():
                continue
            if needle:
                hay = " ".join(
                    [
                        s.operation_id or "",
                        s.method,
                        s.path_template,
                        s.summary,
                        s.tags,
                    ]
                ).lower()
                if needle not in hay:
                    continue
            out.append(s)
            if len(out) >= int(limit):
                break
        return out


def _dns_sensitivity_override(*, method: str, path: str) -> str | None:
    m = str(method or "").upper().strip()
    p = str(path or "").strip()
    if m == "GET" and p == "/zones/{zone_id}/dns_records/export":
        return "sensitive_read"
    rest = _account_scoped_rest(p)
    if rest is not None and rest.startswith("secondary_dns/tsigs"):
        if m == "GET":
            return "sensitive_read"
        if m in {"POST", "PUT", "PATCH"}:
            return "sensitive_write_result"
    return None


def _phase_7c_sensitivity_override(
    *,
    method: str,
    path: str,
    operation_id: str | None,
) -> str | None:
    m = str(method or "").upper().strip()
    p = str(path or "").strip()
    op = str(operation_id or "").strip() or None
    rest = _account_scoped_rest(p) or ""

    # Workers KV bulk get is a POST that returns values (sensitive, read-like).
    if op == "workers-kv-namespace-get-multiple-key-value-pairs" or (m == "POST" and rest == "storage/kv/namespaces/{namespace_id}/bulk/get"):
        return "sensitive_read"

    # Queues pull returns message bodies (sensitive, read-like).
    if op == "queues-pull-messages" or (m == "POST" and rest == "queues/{queue_id}/messages/pull"):
        return "sensitive_read"

    # D1 query/export responses can include database contents (sensitive).
    if rest.startswith("d1/"):
        if m == "POST" and p.endswith("/query"):
            return "sensitive_read"
        if m == "POST" and p.endswith("/raw"):
            return "sensitive_read"
        if m == "POST" and p.endswith("/export"):
            return "sensitive_read"
        if m == "POST" and p.endswith("/import"):
            return "sensitive_read"

    # Hyperdrive configs may include connection details/credentials (sensitive).
    if rest.startswith("hyperdrive/configs"):
        return "sensitive_read"

    # Pipelines validate_sql can echo user SQL and pipeline diagnostics (sensitive, read-like).
    if op == "postV4AccountsByAccount_idPipelinesV1Validate_sql" or (
        m == "POST" and rest == "pipelines/v1/validate_sql"
    ):
        return "sensitive_read"

    # R2 temp creds returns secret-bearing credentials (file-only + ack).
    if op == "r2-create-temp-access-credentials" or (m == "POST" and rest == "r2/temp-access-credentials"):
        return "sensitive_write_result"

    # R2 catalog credential endpoints may return secrets (conservative).
    if op == "store-credentials" or p.endswith("/credential"):
        if m == "POST" and rest.startswith("r2-catalog/"):
            return "sensitive_write_result"

    # Secrets Store: treat get-by-id as sensitive, and writes as secret-bearing unless proven otherwise.
    if op == "secrets-store-get-by-id":
        return "sensitive_read"
    if op in {"secrets-store-secret-create", "secrets-store-patch-by-id", "secrets-store-duplicate-by-id"}:
        return "sensitive_write_result"

    # Workers Tails: Start Tail returns a WS URL with a secret-bearing token.
    if op == "worker-tail-logs-start-tail" or (m == "POST" and rest == "workers/scripts/{script_name}/tails"):
        return "sensitive_write_result"

    # Workers Observability Telemetry: telemetry query results can include stored logs and other event data (PII-risk).
    # Treat the entire surface as sensitive file-only output (never printed).
    if p.startswith("/telemetry/"):
        return "sensitive_read"
    if rest.startswith("workers/observability/telemetry/"):
        return "sensitive_read"

    return None


def _phase_7b_sensitivity_override(*, method: str, path: str, operation_id: str | None) -> str | None:
    _ = operation_id
    m = str(method or "").upper().strip()
    p = str(path or "").strip()
    # Snippet content is sensitive; never print, file-only.
    if m == "GET" and p == "/zones/{zone_id}/snippets/{snippet_name}/content":
        return "sensitive_read"
    return None


def _phase_7d_sensitivity_override(
    *,
    method: str,
    path: str,
    operation_id: str | None,
) -> str | None:
    m = str(method or "").upper().strip()
    p = str(path or "").strip()
    op = str(operation_id or "").strip() or None
    rest = _account_scoped_rest(p) or ""

    # Logpush configs commonly include destination configuration; treat all Logpush endpoints as sensitive file-only output.
    if rest.startswith("logpush") or p.startswith("/zones/{zone_id}/logpush"):
        return "sensitive_read"

    # Audit logs can contain user identifiers and event details; treat as sensitive file-only reads.
    if m == "GET" and (rest in {"audit_logs", "logs/audit"} or p == "/user/audit_logs"):
        return "sensitive_read"

    # Zone logs endpoints can contain request/visitor metadata; treat as sensitive file-only reads.
    if m == "GET" and (p.startswith("/zones/{zone_id}/logs/received") or p.startswith("/zones/{zone_id}/logs/rayids/")):
        return "sensitive_read"

    # Request Tracer is a read-like POST returning trace details; treat as sensitive file-only output.
    if (op == "account-request-tracer-request-trace") or (m == "POST" and rest == "request-tracer/trace"):
        return "sensitive_read"

    return None


def _phase_7e_1_sensitivity_override(*, method: str, path: str) -> str | None:
    _ = method
    p = str(path or "").strip()

    # Phase 7E-1: Custom Hostnames + SSL/TLS are sensitive output surfaces.
    # Conservative: treat all methods under these paths as file-only (never printed).
    if p.startswith("/zones/{zone_id}/custom_hostnames"):
        return "sensitive_read"
    if p.startswith("/zones/{zone_id}/ssl/"):
        return "sensitive_read"
    if p == "/zones/{zone_id}/settings/ssl_automatic_mode":
        return "sensitive_read"
    return None


def _phase_7e_2_sensitivity_override(*, method: str, path: str) -> str | None:
    _ = method
    p = str(path or "").strip()

    # Phase 7E-2: Load Balancing endpoints may include origin/health metadata; treat as file-only output.
    # Conservative: all methods under this prefix require --apply + --out (and --yes for state writes).
    rest = _account_scoped_rest(p)
    if rest is not None and rest.startswith("load_balancers/"):
        return "sensitive_read"
    return None


def _phase_7e_3_sensitivity_override(*, method: str, path: str) -> str | None:
    _ = method
    p = str(path or "").strip()

    # Phase 7E-3: Zaraz zone settings can expose full analytics/marketing configuration.
    # Conservative: treat all methods as file-only output.
    if p.startswith("/zones/{zone_id}/settings/zaraz/"):
        return "sensitive_read"
    return None


def _phase_7e_4_sensitivity_override(*, method: str, path: str) -> str | None:
    _ = method
    p = str(path or "").strip()

    # Phase 7E-4: Registrar domain objects can include registrant PII.
    # Conservative: treat all methods under this prefix as file-only output.
    rest = _account_scoped_rest(p)
    if rest is not None and rest.startswith("registrar/"):
        return "sensitive_read"
    return None


def _phase_7e_5_sensitivity_override(*, method: str, path: str) -> str | None:
    m = str(method or "").upper().strip()
    p = str(path or "").strip()
    rest = _account_scoped_rest(p)

    # Phase 7E-5: Turnstile widget configuration is sensitive output (file-only).
    if rest is None or not rest.startswith("challenges/widgets"):
        return None

    # Create + rotate_secret can return a secret (often shown once).
    if (m == "POST" and rest == "challenges/widgets") or (
        m == "POST" and rest == "challenges/widgets/{sitekey}/rotate_secret"
    ):
        return "sensitive_write_result"

    return "sensitive_read"


def _phase_7e_6_sensitivity_override(*, method: str, path: str) -> str | None:
    _ = method
    p = str(path or "").strip()
    rest = _account_scoped_rest(p)

    # Phase 7E-6: Email Routing can contain recipient addresses/patterns (PII).
    # Conservative: treat all methods under these paths as file-only output.
    if rest is not None and rest.startswith("email/routing"):
        return "sensitive_read"
    if p.startswith("/zones/{zone_id}/email/routing"):
        return "sensitive_read"
    return None


def _phase_7f_sensitivity_override(*, method: str, path: str, operation_id: str | None) -> str | None:
    """
    Phase 7F: Account access management (Account Members + Account Roles).

    Members endpoints return PII (email) but the upstream OpenAPI snapshot does not mark them as PII.
    We override sensitivity so:
    - list/details are treated as sensitive reads (file-only output; never printed)
    - write results are treated as sensitive (may include email)
    """
    m = str(method or "").upper().strip()
    p = str(path or "").strip()
    op = str(operation_id or "").strip() or None
    rest = _account_scoped_rest(p)

    if op in {"account-members-list-members", "account-members-member-details"}:
        return "sensitive_read"
    if op in {"account-members-add-member", "account-members-update-member", "account-members-remove-member"}:
        return "sensitive_write_result"

    # Fallback: match deterministic method+path when operationId is absent.
    if rest is not None and (m, rest) in {
        ("GET", "members"),
        ("GET", "members/{member_id}"),
    }:
        return "sensitive_read"
    if rest is not None and (m, rest) in {
        ("POST", "members"),
        ("PUT", "members/{member_id}"),
        ("DELETE", "members/{member_id}"),
    }:
        return "sensitive_write_result"

    return None


def _phase_8a_sensitivity_override(*, method: str, path: str, operation_id: str | None) -> str | None:
    m = str(method or "").upper().strip()
    p = str(path or "").strip()
    op = str(operation_id or "").strip() or None
    rest = _account_scoped_rest(p)

    # Phase 8A: Workflows instance describe includes logs/status and is treated as sensitive file-only output.
    if op == "wor-describe-workflow-instance":
        return "sensitive_read"
    if rest is not None and (m, rest) == ("GET", "workflows/{workflow_name}/instances/{instance_id}"):
        return "sensitive_read"

    return None


def _phase_9_sensitivity_override(*, method: str, path: str) -> str | None:
    _ = method
    p = str(path or "").strip()

    # Phase 9: Pages objects can include environment variables (including secret/plaintext values).
    # Conservative: treat all methods under this prefix as file-only output (never printed).
    rest = _account_scoped_rest(p)
    if rest is not None and rest.startswith("pages/"):
        return "sensitive_read"
    return None


def _phase_10_sensitivity_override(*, method: str, path: str) -> str | None:
    m = str(method or "").upper().strip()
    p = str(path or "").strip()
    rest = _account_scoped_rest(p)

    # Phase 10: Cloudflare Images has secret-bearing/sensitive surfaces:
    # - blob returns raw image bytes
    # - direct_upload returns a time-limited upload URL
    # - signing keys surface returns/manages signing keys
    if rest is not None and (m, rest) in {
        ("GET", "images/v1/{image_id}/blob"),
        ("POST", "images/v2/direct_upload"),
    }:
        return "sensitive_read"
    # Stream direct upload returns time-limited upload URLs/tokens (file-only output).
    if rest is not None and (m, rest) == ("POST", "stream/direct_upload"):
        return "sensitive_read"
    if rest is not None and rest.startswith("images/v1/keys"):
        return "sensitive_read"
    return None


def _phase_11_ai_gateway_sensitivity_override(*, method: str, path: str) -> str | None:
    m = str(method or "").upper().strip()
    p = str(path or "").strip()

    rest = _account_scoped_rest(p)
    if rest is None or not rest.startswith("ai-gateway/"):
        return None
    rest = rest[len("ai-gateway/") :]

    # Logs can contain prompts/responses and must be file-only output (never printed).
    if "/logs" in rest:
        return "sensitive_read"

    # Provider configs are especially sensitive: reads may include configuration; writes may return secrets/tokens.
    if "/provider_configs" in rest:
        if m == "GET":
            return "sensitive_read"
        return "sensitive_write_result"

    # Datasets and evaluations may contain prompt/output-bearing data (conservative: file-only for all methods).
    if rest.startswith("evaluation-types") or "/datasets" in rest or "/evaluations" in rest:
        return "sensitive_read"

    return None


def phase_12_vectorize_sensitivity_override(*, method: str, path: str) -> str | None:
    _ = method
    p = str(path or "").strip()
    rest = _account_scoped_rest(p)
    if rest is not None and rest.startswith("vectorize/"):
        return "sensitive_read"
    return None


def phase_13_autorag_sensitivity_override(*, method: str, path: str) -> str | None:
    _ = method
    p = str(path or "").strip()
    rest = _account_scoped_rest(p)
    if rest is not None and rest.startswith("autorag/"):
        return "sensitive_read"
    return None


def phase_14_workers_ai_sensitivity_override(*, method: str, path: str) -> str | None:
    _ = method
    p = str(path or "").strip()
    rest = _account_scoped_rest(p)
    if rest is not None and rest.startswith("ai/"):
        return "sensitive_read"
    return None


def phase_15_ai_search_sensitivity_override(*, method: str, path: str, operation_id: str | None) -> str | None:
    m = str(method or "").upper().strip()
    p = str(path or "").strip()
    op = str(operation_id or "").strip() or None
    rest = _account_scoped_rest(p)

    if rest is None or not rest.startswith("ai-search/"):
        return None

    # Token create/update can return secrets and are treated as secret-bearing write results.
    if op in {"ai-search-create-tokens", "ai-search-update-tokens"} or (
        rest.startswith("ai-search/tokens") and m in {"POST", "PUT"}
    ):
        return "sensitive_write_result"

    # Everything else is file-only output (never printed) and hidden by default.
    return "sensitive_read"


def phase_16_email_security_sensitivity_override(*, method: str, path: str, operation_id: str | None) -> str | None:
    _ = method
    _ = operation_id
    p = str(path or "").strip()
    rest = _account_scoped_rest(p)

    # Phase 16: Email Security endpoints can return raw email content/trace/detections and other message metadata.
    # Conservative: treat all Email Security operations as sensitive file-only output (never printed).
    if rest is not None and rest.startswith("email-security/"):
        return "sensitive_read"

    # Phase 16: DLP Email scanner rules/config can include patterns and other sensitive configuration.
    if rest is not None and rest.startswith("dlp/email/"):
        return "sensitive_read"

    # Phase 16: Radar Email Security/Routing analytics are scoped to "User Details" (PII-risk).
    if p.startswith("/radar/email/security/") or p.startswith("/radar/email/routing/"):
        return "sensitive_read"

    return None


def phase_21_radar_sensitivity_override(*, method: str, path: str) -> str | None:
    _ = method
    p = str(path or "").strip()

    # Phase 21: Cloudflare Radar analytics can include user-identifying details.
    # Conservative: treat all Radar operations as sensitive file-only output (never printed),
    # and hide them from `openapi list` unless --include-sensitive.
    if p.startswith("/radar/"):
        return "sensitive_read"
    return None


def phase_28_live_surface_sensitivity_override(*, method: str, path: str) -> str | None:
    _ = method
    p = str(path or "").strip()

    # Live-docs drift fixes: newly surfaced endpoints that can expose content, diagnostics, or browser/session data
    # stay file-only until a narrower review proves otherwise.
    if p.startswith("/accounts/{account_id}/browser-rendering/"):
        return "sensitive_read"
    if p.startswith("/accounts/{account_id}/vuln_scanner/"):
        return "sensitive_read"
    if p.startswith("/accounts/{account_id}/cloudforce-one/v2/brand-protection/"):
        return "sensitive_read"
    if p.startswith("/accounts/{account_id}/warp_connector/"):
        return "sensitive_read"
    if p.startswith("/accounts/{account_id}/custom_pages"):
        return "sensitive_read"
    if p.startswith("/zones/{zone_id}/custom_pages"):
        return "sensitive_read"
    if p.startswith("/accounts/{account_id}/email/sending/"):
        return "sensitive_read"
    if p.startswith("/zones/{zone_id}/environments"):
        return "sensitive_read"
    return None


def _strip_ticks(s: str) -> str:
    t = str(s or "").strip()
    if t.startswith("`") and t.endswith("`") and len(t) >= 2:
        return t[1:-1].strip()
    return t


def _split_md_row(row_line: str) -> list[str]:
    s = str(row_line or "").strip()
    if not s.startswith("|"):
        return []
    s = s.strip().strip("|")
    cols: list[str] = []
    cur: list[str] = []
    esc = False
    for ch in s:
        if esc:
            cur.append(ch)
            esc = False
            continue
        if ch == "\\":
            esc = True
            continue
        if ch == "|":
            cols.append("".join(cur).strip())
            cur = []
            continue
        cur.append(ch)
    if esc:
        cur.append("\\")
    cols.append("".join(cur).strip())
    return cols


def _parse_coverage_table(md_path: Path) -> list[dict[str, str]]:
    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    header_idx = None
    for i, line in enumerate(lines):
        if line.startswith("| Status |") and "| Method |" in line and "| Path |" in line:
            header_idx = i
            break
    if header_idx is None:
        raise ToolError(f"Could not find coverage table header in: {md_path}")

    header_cols = _split_md_row(lines[header_idx])
    col_index = {name: idx for idx, name in enumerate(header_cols)}
    if "Method" not in col_index or "Path" not in col_index:
        raise ToolError(f"Coverage table is missing required columns in: {md_path}")

    rows: list[dict[str, str]] = []
    for line in lines[header_idx + 2 :]:
        if not line.startswith("|"):
            break
        if line.startswith("|---"):
            continue
        cols = _split_md_row(line)
        if len(cols) < len(header_cols):
            continue
        if len(cols) > len(header_cols):
            cols = cols[: len(header_cols)]
        rows.append({header_cols[j]: cols[j] for j in range(len(header_cols))})
    return rows


def classify_operation_sensitivity(
    *,
    area: str,
    method: str,
    path: str,
    summary: str,
    operation_id: str | None,
    api_token_groups: str,
) -> str:
    sensitivity = "none"
    if _is_sensitive_read(
        method=method,
        path=path,
        summary=summary,
        operation_id=operation_id or "",
        api_token_groups=api_token_groups,
    ):
        sensitivity = "sensitive_read"
    elif _is_sensitive_write_result(
        method=method,
        path=path,
        summary=summary,
        operation_id=operation_id or "",
        api_token_groups=api_token_groups,
    ):
        sensitivity = "sensitive_write_result"

    override = _dns_sensitivity_override(method=method, path=path)
    if override:
        sensitivity = override

    override_7c = _phase_7c_sensitivity_override(method=method, path=path, operation_id=operation_id)
    if override_7c:
        sensitivity = override_7c
    override_7d = _phase_7d_sensitivity_override(method=method, path=path, operation_id=operation_id)
    if override_7d:
        sensitivity = override_7d

    override_7b = _phase_7b_sensitivity_override(method=method, path=path, operation_id=operation_id)
    if override_7b:
        sensitivity = override_7b

    override_7e_1 = _phase_7e_1_sensitivity_override(method=method, path=path)
    if override_7e_1:
        sensitivity = override_7e_1
    override_7e_2 = _phase_7e_2_sensitivity_override(method=method, path=path)
    if override_7e_2:
        sensitivity = override_7e_2

    override_7e_3 = _phase_7e_3_sensitivity_override(method=method, path=path)
    if override_7e_3:
        sensitivity = override_7e_3

    override_7e_4 = _phase_7e_4_sensitivity_override(method=method, path=path)
    if override_7e_4:
        sensitivity = override_7e_4

    override_7e_5 = _phase_7e_5_sensitivity_override(method=method, path=path)
    if override_7e_5:
        sensitivity = override_7e_5

    override_7e_6 = _phase_7e_6_sensitivity_override(method=method, path=path)
    if override_7e_6:
        sensitivity = override_7e_6

    override_7f = _phase_7f_sensitivity_override(method=method, path=path, operation_id=operation_id)
    if override_7f:
        sensitivity = override_7f

    override_8a = _phase_8a_sensitivity_override(method=method, path=path, operation_id=operation_id)
    if override_8a:
        sensitivity = override_8a

    override_9 = _phase_9_sensitivity_override(method=method, path=path)
    if override_9:
        sensitivity = override_9

    override_10 = _phase_10_sensitivity_override(method=method, path=path)
    if override_10:
        sensitivity = override_10

    override_11 = _phase_11_ai_gateway_sensitivity_override(method=method, path=path)
    if override_11:
        sensitivity = override_11

    override_12 = phase_12_vectorize_sensitivity_override(method=method, path=path)
    if override_12:
        sensitivity = override_12

    override_13 = phase_13_autorag_sensitivity_override(method=method, path=path)
    if override_13:
        sensitivity = override_13

    override_14 = phase_14_workers_ai_sensitivity_override(method=method, path=path)
    if override_14:
        sensitivity = override_14

    override_15 = phase_15_ai_search_sensitivity_override(method=method, path=path, operation_id=operation_id)
    if override_15:
        sensitivity = override_15

    override_16 = phase_16_email_security_sensitivity_override(method=method, path=path, operation_id=operation_id)
    if override_16:
        sensitivity = override_16

    override_21 = phase_21_radar_sensitivity_override(method=method, path=path)
    if override_21:
        sensitivity = override_21

    override_28 = phase_28_live_surface_sensitivity_override(method=method, path=path)
    if override_28:
        sensitivity = override_28

    op_id = str(operation_id or "").strip()
    if op_id == "origin-ca-create-certificate" and method == "POST" and path == "/certificates":
        sensitivity = "sensitive_write_result"
    if op_id.startswith("secrets-store-system-") or path.startswith("/system/accounts/"):
        sensitivity = "sensitive_read" if method == "GET" else "sensitive_write_result"

    if area in {"user", "organizations"}:
        if sensitivity == "none":
            sensitivity = "sensitive_read"

    if area == "system_misc":
        if method == "GET" and path in {"/accounts", "/zones", "/ips", "/live", "/ready"}:
            pass
        elif sensitivity == "none":
            sensitivity = "sensitive_read"

    if area == "accounts_get":
        if method != "GET":
            raise ToolError(
                "Accounts GET allowlist ledger must only contain GET operations. "
                f"Found: {method} {path} (operation_id={operation_id or ''})"
            )
        sensitivity = "sensitive_read"

    if area == "zones_get":
        if method != "GET":
            raise ToolError(
                "Zones GET allowlist ledger must only contain GET operations. "
                f"Found: {method} {path} (operation_id={operation_id or ''})"
            )
        if not str(path or "").startswith("/zones/"):
            raise ToolError(
                "Zones GET allowlist ledger must only contain /zones/ operations. "
                f"Found: {method} {path} (operation_id={operation_id or ''})"
            )
        if str(path or "").strip() == "/zones":
            raise ToolError(
                'Zones GET allowlist ledger must not include "/zones" (requires /zones/ prefix). '
                f"Found: {method} {path} (operation_id={operation_id or ''})"
            )
        sensitivity = "sensitive_read"

    return sensitivity


def _spec_from_fields(
    *,
    area: str,
    method: str,
    path: str,
    operation_id: str | None,
    summary: str,
    tags: str,
    deprecated: bool,
    api_token_groups: str,
) -> OperationSpec:
    return OperationSpec(
        area=area,
        method=method,
        path_template=path,
        operation_id=operation_id,
        summary=summary,
        tags=tags,
        deprecated=deprecated,
        api_token_groups=api_token_groups,
        sensitivity=classify_operation_sensitivity(
            area=area,
            method=method,
            path=path,
            summary=summary,
            operation_id=operation_id,
            api_token_groups=api_token_groups,
        ),
    )


def _load_specs_from_coverage_ledgers(*, include_dns: bool) -> list[OperationSpec]:
    docs_dir = _tool_root() / "docs"
    workers_md = docs_dir / "api_coverage_workers_platform.md"
    zt_md = docs_dir / "api_coverage_zero_trust.md"
    if not workers_md.exists() or not zt_md.exists():
        raise ToolError(
            "Missing tool-local coverage ledgers required for allowlisted operations: "
            f"{workers_md} and/or {zt_md}."
        )

    ledgers = sorted(
        [
            p
            for p in docs_dir.glob("api_coverage_*.md")
            if p.name not in {"api_coverage.md", "api_coverage_live_official.md"}
        ],
        key=lambda p: p.name,
    )
    ledger_paths: list[tuple[str, Path]] = []
    for md_path in ledgers:
        name = md_path.name
        if not name.startswith("api_coverage_") or not name.endswith(".md"):
            continue
        area = name[len("api_coverage_") : -len(".md")].strip()
        if not area:
            continue
        if area == "dns" and not include_dns:
            continue
        ledger_paths.append((area, md_path))

    ledger_paths = (
        [x for x in ledger_paths if x[0] not in {"accounts_get", "zones_get"}]
        + [x for x in ledger_paths if x[0] == "zones_get"]
        + [x for x in ledger_paths if x[0] == "accounts_get"]
    )

    seen_method_path: set[tuple[str, str]] = set()
    specs: list[OperationSpec] = []
    for area, md_path in ledger_paths:
        rows = _parse_coverage_table(md_path)
        for r in rows:
            method = str(r.get("Method") or "").upper().strip()
            path = _strip_ticks(str(r.get("Path") or ""))
            operation_id = _strip_ticks(str(r.get("OperationId") or "")) or None
            summary = str(r.get("Summary") or "").strip()
            tags = str(r.get("Tags") or "").strip()
            api_token_groups = str(r.get("API token groups") or r.get("Permissions") or "").strip()
            deprecated = summary.strip().startswith("[DEPRECATED]")
            if not method or not path:
                continue
            key = (method, path)
            if key in seen_method_path:
                continue
            seen_method_path.add(key)
            specs.append(
                _spec_from_fields(
                    area=area,
                    method=method,
                    path=path,
                    operation_id=operation_id,
                    summary=summary,
                    tags=tags,
                    deprecated=deprecated,
                    api_token_groups=api_token_groups,
                )
            )
    return specs


def _load_specs_from_live_inventory_json(*, include_dns: bool) -> list[OperationSpec]:
    inventory_path = _tool_root() / "docs" / "_generated" / "live_official_api_inventory.json"
    raw = inventory_path.read_text(encoding="utf-8")
    payload = dict() if not raw else json.loads(raw)
    rows = payload.get("operations")
    if not isinstance(rows, list):
        raise ToolError(f"Live inventory JSON is missing an operations list: {inventory_path}")

    seen_method_path: set[tuple[str, str]] = set()
    specs: list[OperationSpec] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        area = str(row.get("area") or "").strip()
        method = str(row.get("method") or "").upper().strip()
        path = str(row.get("path_template") or row.get("path") or "").strip()
        operation_id = str(row.get("operation_id") or "").strip() or None
        summary = str(row.get("summary") or row.get("title") or "").strip()
        tags = str(row.get("tags") or "").strip()
        api_token_groups = str(row.get("api_token_groups") or "").strip()
        deprecated = bool(row.get("deprecated", False))
        if not area or not method or not path:
            continue
        if area == "dns" and not include_dns:
            continue
        key = (method, path)
        if key in seen_method_path:
            continue
        seen_method_path.add(key)
        specs.append(
            _spec_from_fields(
                area=area,
                method=method,
                path=path,
                operation_id=operation_id,
                summary=summary,
                tags=tags,
                deprecated=deprecated,
                api_token_groups=api_token_groups,
            )
        )
    return specs


def load_allowlisted_operation_index(*, include_dns: bool = True) -> OperationIndex:
    """
    Load the operation index from the committed live official inventory when present.

    Fallback remains the historical markdown coverage ledgers so local development can regenerate the
    live inventory without a bootstrap problem.
    """
    live_inventory = _tool_root() / "docs" / "_generated" / "live_official_api_inventory.json"
    if live_inventory.exists():
        specs = _load_specs_from_live_inventory_json(include_dns=include_dns)
    else:
        specs = _load_specs_from_coverage_ledgers(include_dns=include_dns)

    specs.sort(key=lambda s: (s.area, s.path_template, s.method, s.operation_id or ""))
    return OperationIndex(specs=specs)


def load_workers_and_zero_trust_index() -> OperationIndex:
    """
    Backward-compatible wrapper: load Workers platform + Zero Trust allowlist only.

    New callers should use load_allowlisted_operation_index().
    """
    return load_allowlisted_operation_index(include_dns=False)
