from __future__ import annotations

import argparse
import sys
import traceback

from . import __version__
from .audit_log import AuditLogger
from .commands import ad_accounts as ad_accounts_cmd
from .commands import ad_sets as ad_sets_cmd
from .commands import ads as ads_cmd
from .commands import auth as auth_cmd
from .commands import campaigns as campaigns_cmd
from .commands import creatives as creatives_cmd
from .commands import images as images_cmd
from .commands import insights as insights_cmd
from .commands import onboarding as onboarding_cmd
from .commands import previews as previews_cmd
from .commands import presets as presets_cmd
from .commands import snapshot as snapshot_cmd
from .commands import videos as videos_cmd
from .config import load_config
from .errors import NotSupportedError, RemoteApiError, ToolError, ValidationError
from .graph import GraphClient
from .http import HttpClient
from .output import Output


def _argv_output_mode(argv: list[str]) -> str:
    for i, tok in enumerate(argv):
        if tok == "--output" and i + 1 < len(argv):
            return str(argv[i + 1])
        if tok.startswith("--output="):
            return tok.split("=", 1)[1]
    return "json"


def _argv_wants_json(argv: list[str]) -> bool:
    return _argv_output_mode(argv) != "text"


def build_parser() -> argparse.ArgumentParser:
    class _JsonAwareParser(argparse.ArgumentParser):
        def parse_args(self, args=None, namespace=None):  # type: ignore[override]
            self._raw_args = list(args) if args is not None else sys.argv[1:]
            return super().parse_args(args=args, namespace=namespace)

        def error(self, message: str) -> None:  # type: ignore[override]
            raw = getattr(self, "_raw_args", sys.argv[1:])
            if _argv_wants_json(list(raw)):
                raise ValidationError(message)
            super().error(message)

    p = _JsonAwareParser(prog="meta-ads-api-tool")
    p.add_argument("--version", action="store_true", help="Print version and exit")
    p.add_argument("--env-file", default=".env", help="Optional .env file path (default: .env)")
    p.add_argument("--timeout-s", type=float, default=None, help="Override timeout seconds")
    p.add_argument("--verbose", action="store_true", help="Verbose HTTP logging to stderr (tokens redacted)")
    p.add_argument("--debug", action="store_true", help="Show stack traces on errors")
    p.add_argument("--output", choices=("json", "text"), default="json", help="Output format (default: json)")
    p.add_argument("--log-file", default=None, help="Optional audit log path (JSONL)")
    p.add_argument("--ad-account-id", default=None, help="Optional ad account id (numeric or act_<id>)")
    p.add_argument("--api-version", default=None, help="Override Graph API version (default: from .env or v24.0)")

    sub = p.add_subparsers(dest="cmd", required=False)

    onboarding = sub.add_parser("onboarding", help="First-time setup checklist")
    onboarding.add_argument("--no-write-env", action="store_true", help="Do not write the .env file")
    onboarding.set_defaults(func=onboarding_cmd.cmd_onboarding)

    auth = sub.add_parser("auth", help="Authentication checks")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True)
    auth_check = auth_sub.add_parser("check", help="Validate token via a minimal GET")
    auth_check.set_defaults(func=auth_cmd.cmd_auth_check)

    presets = sub.add_parser("presets", help="Built-in presets for common workflows")
    presets_sub = presets.add_subparsers(dest="presets_cmd", required=True)
    presets_list = presets_sub.add_parser("list", help="List available presets")
    presets_list.set_defaults(func=presets_cmd.cmd_presets_list)
    presets_show = presets_sub.add_parser("show", help="Show a preset (resolved config)")
    presets_show.add_argument("--preset", required=True, help="Preset id (from `presets list`)")
    presets_show.set_defaults(func=presets_cmd.cmd_presets_show)

    snapshot = sub.add_parser("snapshot", help="Analysis-ready snapshot exports (GET-only)")
    snapshot_sub = snapshot.add_subparsers(dest="snapshot_cmd", required=True)
    snap_export = snapshot_sub.add_parser("export", help="Export a snapshot pack (manifest + JSONL tables)")
    snap_export.add_argument("--ad-account-id", required=False, help="Ad account id (numeric or act_<id>)")
    snap_export.add_argument("--preset", required=True, help="Preset id (from `presets list`)")
    snap_export.add_argument("--out-dir", required=True, help="Output directory to create the snapshot pack under")
    snap_export.add_argument("--run-id", default=None, help="Optional run id (deterministic pack name if provided)")
    snap_export.add_argument("--strict", action="store_true", help="Fail the export if any chunk/surface fetch fails")
    snap_export.add_argument(
        "--since",
        default=None,
        help="For snapshot insights: start date (YYYY-MM-DD). Use with --until. Overrides preset/--param.",
    )
    snap_export.add_argument(
        "--until",
        default=None,
        help="For snapshot insights: end date (YYYY-MM-DD). Use with --since. Overrides preset/--param.",
    )
    snap_export.add_argument(
        "--date-preset",
        default=None,
        help="For snapshot insights: Meta date preset (example: last_7d, last_28d). Overrides preset/--param.",
    )
    snap_export.add_argument(
        "--insights-time-increment",
        default=None,
        help="For snapshot insights: time_increment value (example: 1, 7, monthly). Overrides preset/--param.",
    )
    snap_export.add_argument(
        "--insights-breakdown",
        action="append",
        default=[],
        help="For snapshot insights: breakdown dimension (repeatable). Overrides preset/--param.",
    )
    snap_export.add_argument(
        "--insights-action-breakdown",
        action="append",
        default=[],
        help="For snapshot insights: action_breakdowns value (repeatable). Overrides preset/--param.",
    )
    snap_export.add_argument(
        "--insights-action-attribution-window",
        action="append",
        default=[],
        help="For snapshot insights: action_attribution_windows value (repeatable). Overrides preset/--param.",
    )
    snap_export.add_argument(
        "--extra-insights-breakdown-table",
        action="append",
        default=[],
        help="Add extra insights table(s): suffix:breakdowns_csv (example: placement:publisher_platform,platform_position). Repeatable.",
    )
    snap_export.add_argument(
        "--fields-campaigns",
        default=None,
        help="Override preset campaign fields for snapshot export (comma-separated).",
    )
    snap_export.add_argument(
        "--fields-ad-sets",
        default=None,
        help="Override preset ad set fields for snapshot export (comma-separated).",
    )
    snap_export.add_argument(
        "--fields-ads",
        default=None,
        help="Override preset ad fields for snapshot export (comma-separated).",
    )
    snap_export.add_argument(
        "--fields-creatives",
        default=None,
        help="Override preset creative fields for snapshot export (comma-separated).",
    )
    snap_export.add_argument(
        "--fields-insights",
        default=None,
        help="Override preset insights fields for snapshot export (comma-separated).",
    )
    snap_export.add_argument(
        "--download-assets",
        action="store_true",
        help="Opt-in: download creative asset URLs (if present) into the pack under assets/ (default: off)",
    )
    snap_export.add_argument(
        "--assets-overwrite",
        choices=("never", "if_missing", "always"),
        default="if_missing",
        help="When --download-assets is enabled: overwrite policy (default: if_missing)",
    )
    snap_export.add_argument("--limit", type=int, default=100, help="Per-request page size limit (default: 100)")
    snap_export.add_argument("--fields-chunk-size", type=int, default=20, help="Max fields per chunk (default: 20)")
    snap_export.add_argument("--param", action="append", default=[], help="Additional query param (k=v); repeatable")
    snap_export.add_argument("--max-pages", type=int, default=50, help="Max pages to fetch per chunk (default: 50)")
    snap_export.add_argument("--max-items", type=int, default=0, help="Max items to return per chunk (default: 0 = unlimited)")
    snap_export.set_defaults(func=snapshot_cmd.cmd_snapshot_export)

    ad_accounts = sub.add_parser("ad-accounts", help="Ad accounts")
    ad_accounts_sub = ad_accounts.add_subparsers(dest="ad_accounts_cmd", required=True)
    aa_list = ad_accounts_sub.add_parser("list", help="List ad accounts for the token (/me/adaccounts)")
    aa_list.add_argument("--fields", default=None, help="Optional fields (comma-separated)")
    aa_list.add_argument("--param", action="append", default=[], help="Additional query param (k=v); repeatable")
    aa_list.add_argument("--limit", type=int, default=100, help="Page size limit (default: 100)")
    aa_list.add_argument("--max-pages", type=int, default=50, help="Max pages to fetch (default: 50)")
    aa_list.add_argument("--max-items", type=int, default=0, help="Max items to return (default: 0 = unlimited)")
    aa_list.set_defaults(func=ad_accounts_cmd.cmd_ad_accounts_list)

    aa_get = ad_accounts_sub.add_parser("get", help="Get an ad account by id")
    aa_get.add_argument("--ad-account-id", required=False, help="Ad account id (numeric or act_<id>)")
    aa_get.add_argument("--fields", default=None, help="Optional fields (comma-separated)")
    aa_get.add_argument("--param", action="append", default=[], help="Additional query param (k=v); repeatable")
    aa_get.set_defaults(func=ad_accounts_cmd.cmd_ad_accounts_get)

    campaigns = sub.add_parser("campaigns", help="Campaigns")
    campaigns_sub = campaigns.add_subparsers(dest="campaigns_cmd", required=True)
    c_list = campaigns_sub.add_parser("list", help="List campaigns for an ad account")
    c_list.add_argument("--ad-account-id", required=False, help="Ad account id (numeric or act_<id>)")
    c_list.add_argument("--fields", default=None, help="Optional fields (comma-separated)")
    c_list.add_argument("--param", action="append", default=[], help="Additional query param (k=v); repeatable")
    c_list.add_argument("--limit", type=int, default=100, help="Page size limit (default: 100)")
    c_list.add_argument("--max-pages", type=int, default=50, help="Max pages to fetch (default: 50)")
    c_list.add_argument("--max-items", type=int, default=0, help="Max items to return (default: 0 = unlimited)")
    c_list.set_defaults(func=campaigns_cmd.cmd_campaigns_list)

    c_get = campaigns_sub.add_parser("get", help="Get a campaign by id")
    c_get.add_argument("--campaign-id", required=True, help="Campaign id")
    c_get.add_argument("--fields", default=None, help="Optional fields (comma-separated)")
    c_get.add_argument("--param", action="append", default=[], help="Additional query param (k=v); repeatable")
    c_get.set_defaults(func=campaigns_cmd.cmd_campaigns_get)

    ad_sets = sub.add_parser("ad-sets", help="Ad sets")
    ad_sets_sub = ad_sets.add_subparsers(dest="ad_sets_cmd", required=True)
    as_list = ad_sets_sub.add_parser("list", help="List ad sets for an ad account")
    as_list.add_argument("--ad-account-id", required=False, help="Ad account id (numeric or act_<id>)")
    as_list.add_argument("--fields", default=None, help="Optional fields (comma-separated)")
    as_list.add_argument("--param", action="append", default=[], help="Additional query param (k=v); repeatable")
    as_list.add_argument("--limit", type=int, default=100, help="Page size limit (default: 100)")
    as_list.add_argument("--max-pages", type=int, default=50, help="Max pages to fetch (default: 50)")
    as_list.add_argument("--max-items", type=int, default=0, help="Max items to return (default: 0 = unlimited)")
    as_list.set_defaults(func=ad_sets_cmd.cmd_ad_sets_list)

    as_get = ad_sets_sub.add_parser("get", help="Get an ad set by id")
    as_get.add_argument("--ad-set-id", required=True, help="Ad set id")
    as_get.add_argument("--fields", default=None, help="Optional fields (comma-separated)")
    as_get.add_argument("--param", action="append", default=[], help="Additional query param (k=v); repeatable")
    as_get.set_defaults(func=ad_sets_cmd.cmd_ad_sets_get)

    ads = sub.add_parser("ads", help="Ads")
    ads_sub = ads.add_subparsers(dest="ads_cmd", required=True)
    a_list = ads_sub.add_parser("list", help="List ads for an ad account")
    a_list.add_argument("--ad-account-id", required=False, help="Ad account id (numeric or act_<id>)")
    a_list.add_argument("--fields", default=None, help="Optional fields (comma-separated)")
    a_list.add_argument("--param", action="append", default=[], help="Additional query param (k=v); repeatable")
    a_list.add_argument("--limit", type=int, default=100, help="Page size limit (default: 100)")
    a_list.add_argument("--max-pages", type=int, default=50, help="Max pages to fetch (default: 50)")
    a_list.add_argument("--max-items", type=int, default=0, help="Max items to return (default: 0 = unlimited)")
    a_list.set_defaults(func=ads_cmd.cmd_ads_list)

    a_get = ads_sub.add_parser("get", help="Get an ad by id")
    a_get.add_argument("--ad-id", required=True, help="Ad id")
    a_get.add_argument("--fields", default=None, help="Optional fields (comma-separated)")
    a_get.add_argument("--param", action="append", default=[], help="Additional query param (k=v); repeatable")
    a_get.set_defaults(func=ads_cmd.cmd_ads_get)

    creatives = sub.add_parser("creatives", help="Ad creatives")
    creatives_sub = creatives.add_subparsers(dest="creatives_cmd", required=True)
    cr_list = creatives_sub.add_parser("list", help="List creatives for an ad account")
    cr_list.add_argument("--ad-account-id", required=False, help="Ad account id (numeric or act_<id>)")
    cr_list.add_argument("--fields", default=None, help="Optional fields (comma-separated)")
    cr_list.add_argument("--param", action="append", default=[], help="Additional query param (k=v); repeatable")
    cr_list.add_argument("--limit", type=int, default=100, help="Page size limit (default: 100)")
    cr_list.add_argument("--max-pages", type=int, default=50, help="Max pages to fetch (default: 50)")
    cr_list.add_argument("--max-items", type=int, default=0, help="Max items to return (default: 0 = unlimited)")
    cr_list.set_defaults(func=creatives_cmd.cmd_creatives_list)

    cr_get = creatives_sub.add_parser("get", help="Get a creative by id")
    cr_get.add_argument("--creative-id", required=True, help="Creative id")
    cr_get.add_argument("--fields", default=None, help="Optional fields (comma-separated)")
    cr_get.add_argument("--param", action="append", default=[], help="Additional query param (k=v); repeatable")
    cr_get.set_defaults(func=creatives_cmd.cmd_creatives_get)

    cr_anatomy = creatives_sub.add_parser("anatomy", help="Fetch a creative and emit a normalized anatomy object (GET-only)")
    cr_anatomy.add_argument("--creative-id", required=True, help="Creative id")
    cr_anatomy.add_argument("--fields", default=None, help="Optional fields (comma-separated)")
    cr_anatomy.add_argument("--param", action="append", default=[], help="Additional query param (k=v); repeatable")
    cr_anatomy.set_defaults(func=creatives_cmd.cmd_creatives_anatomy)

    images = sub.add_parser("images", help="Ad images")
    images_sub = images.add_subparsers(dest="images_cmd", required=True)
    im_list = images_sub.add_parser("list", help="List images for an ad account")
    im_list.add_argument("--ad-account-id", required=False, help="Ad account id (numeric or act_<id>)")
    im_list.add_argument("--fields", default=None, help="Optional fields (comma-separated)")
    im_list.add_argument("--param", action="append", default=[], help="Additional query param (k=v); repeatable")
    im_list.add_argument("--limit", type=int, default=100, help="Page size limit (default: 100)")
    im_list.add_argument("--max-pages", type=int, default=50, help="Max pages to fetch (default: 50)")
    im_list.add_argument("--max-items", type=int, default=0, help="Max items to return (default: 0 = unlimited)")
    im_list.set_defaults(func=images_cmd.cmd_images_list)

    im_get = images_sub.add_parser("get", help="Get an image by id")
    im_get.add_argument("--image-id", required=True, help="Image id")
    im_get.add_argument("--fields", default=None, help="Optional fields (comma-separated)")
    im_get.add_argument("--param", action="append", default=[], help="Additional query param (k=v); repeatable")
    im_get.set_defaults(func=images_cmd.cmd_images_get)

    videos = sub.add_parser("videos", help="Ad videos")
    videos_sub = videos.add_subparsers(dest="videos_cmd", required=True)
    v_list = videos_sub.add_parser("list", help="List videos for an ad account")
    v_list.add_argument("--ad-account-id", required=False, help="Ad account id (numeric or act_<id>)")
    v_list.add_argument("--fields", default=None, help="Optional fields (comma-separated)")
    v_list.add_argument("--param", action="append", default=[], help="Additional query param (k=v); repeatable")
    v_list.add_argument("--limit", type=int, default=100, help="Page size limit (default: 100)")
    v_list.add_argument("--max-pages", type=int, default=50, help="Max pages to fetch (default: 50)")
    v_list.add_argument("--max-items", type=int, default=0, help="Max items to return (default: 0 = unlimited)")
    v_list.set_defaults(func=videos_cmd.cmd_videos_list)

    v_get = videos_sub.add_parser("get", help="Get a video by id")
    v_get.add_argument("--video-id", required=True, help="Video id")
    v_get.add_argument("--fields", default=None, help="Optional fields (comma-separated)")
    v_get.add_argument("--param", action="append", default=[], help="Additional query param (k=v); repeatable")
    v_get.set_defaults(func=videos_cmd.cmd_videos_get)

    previews = sub.add_parser("previews", help="Creative previews (GET-only)")
    previews_sub = previews.add_subparsers(dest="previews_cmd", required=True)
    p_get = previews_sub.add_parser("get", help="Get creative previews via the /previews edge (GET-only)")
    p_get.add_argument("--creative-id", required=True, help="Creative id")
    p_get.add_argument("--ad-format", default=None, help="Optional ad_format (example: DESKTOP_FEED_STANDARD)")
    p_get.add_argument("--param", action="append", default=[], help="Additional query param (k=v); repeatable")
    p_get.set_defaults(func=previews_cmd.cmd_previews_get)

    insights = sub.add_parser("insights", help="Insights / reporting")
    insights_sub = insights.add_subparsers(dest="insights_cmd", required=True)
    i_get = insights_sub.add_parser("get", help="Fetch insights (GET-only)")
    i_get.add_argument("--ad-account-id", required=False, help="Ad account id (numeric or act_<id>)")
    i_get.add_argument("--level", required=True, help="account|campaign|adset|ad")
    i_get.add_argument("--fields", default=None, help="Optional fields (comma-separated)")
    i_get.add_argument("--since", default=None, help="Start date (YYYY-MM-DD)")
    i_get.add_argument("--until", default=None, help="End date (YYYY-MM-DD)")
    i_get.add_argument("--breakdown", action="append", default=[], help="Breakdown name; repeatable")
    i_get.add_argument("--time-increment", default=None, help="Optional time_increment (example: 1, 7, all_days)")
    i_get.add_argument("--action-breakdown", action="append", default=[], help="action_breakdowns value; repeatable")
    i_get.add_argument(
        "--action-attribution-window",
        action="append",
        default=[],
        help="action_attribution_windows value; repeatable (example: 1d_click, 7d_click, 1d_view)",
    )
    i_get.add_argument("--param", action="append", default=[], help="Additional query param (k=v); repeatable")
    i_get.add_argument("--max-pages", type=int, default=50, help="Max pages to fetch (default: 50)")
    i_get.add_argument("--max-items", type=int, default=0, help="Max items to return (default: 0 = unlimited)")
    i_get.set_defaults(func=insights_cmd.cmd_insights_get)

    i_compare = insights_sub.add_parser("compare", help="Fetch insights for two date ranges with identical settings (GET-only)")
    i_compare.add_argument("--ad-account-id", required=False, help="Ad account id (numeric or act_<id>)")
    i_compare.add_argument("--level", required=True, help="account|campaign|adset|ad")
    i_compare.add_argument("--fields", default=None, help="Optional fields (comma-separated)")
    i_compare.add_argument("--since-a", required=True, help="Start date for range A (YYYY-MM-DD)")
    i_compare.add_argument("--until-a", required=True, help="End date for range A (YYYY-MM-DD)")
    i_compare.add_argument("--since-b", required=True, help="Start date for range B (YYYY-MM-DD)")
    i_compare.add_argument("--until-b", required=True, help="End date for range B (YYYY-MM-DD)")
    i_compare.add_argument("--breakdown", action="append", default=[], help="Breakdown name; repeatable")
    i_compare.add_argument("--time-increment", default=None, help="Optional time_increment (example: 1, 7, all_days)")
    i_compare.add_argument("--action-breakdown", action="append", default=[], help="action_breakdowns value; repeatable")
    i_compare.add_argument(
        "--action-attribution-window",
        action="append",
        default=[],
        help="action_attribution_windows value; repeatable (example: 1d_click, 7d_click, 1d_view)",
    )
    i_compare.add_argument("--param", action="append", default=[], help="Additional query param (k=v); repeatable")
    i_compare.add_argument("--max-pages", type=int, default=50, help="Max pages to fetch (default: 50)")
    i_compare.add_argument("--max-items", type=int, default=0, help="Max items to return (default: 0 = unlimited)")
    i_compare.set_defaults(func=insights_cmd.cmd_insights_compare)

    return p


def _emit_error(out: Output, *, tool: str, version: str, command_str: str, err: Exception) -> None:
    out.set_provenance({"tool": tool, "version": version, "command": command_str})
    out.emit({"ok": False, "error": str(err), "error_type": type(err).__name__})


def main(argv: list[str]) -> int:
    tool = "meta-ads-api-tool"
    out = Output(mode=_argv_output_mode(argv))
    command_str = tool + (" " + " ".join(argv) if argv else "")
    out.set_provenance({"tool": tool, "version": __version__, "command": command_str})

    p = build_parser()
    try:
        args = p.parse_args(argv)
    except ValidationError as e:
        _emit_error(out, tool=tool, version=__version__, command_str=command_str, err=e)
        return 1

    if bool(getattr(args, "version", False)):
        if str(getattr(args, "output", "json")) == "json":
            out.emit({"ok": True, "version": __version__})
        else:
            print(f"{tool} {__version__}")
        return 0

    if not getattr(args, "cmd", None) or not getattr(args, "func", None):
        _emit_error(out, tool=tool, version=__version__, command_str=command_str, err=ValidationError("Missing command"))
        return 1

    audit = AuditLogger(path=str(getattr(args, "log_file", None) or "") or None, enabled=True)
    audit.bind_context({"tool": tool, "version": __version__})

    try:
        cfg = load_config(
            getattr(args, "env_file", ".env"),
            ad_account_id_override=getattr(args, "ad_account_id", None),
            api_version_override=getattr(args, "api_version", None),
        )
        if getattr(args, "timeout_s", None) is not None:
            cfg = cfg.__class__(**{**cfg.__dict__, "timeout_s": float(getattr(args, "timeout_s"))})  # type: ignore[attr-defined]

        http = HttpClient(timeout_s=cfg.timeout_s, verbose=bool(getattr(args, "verbose", False)), user_agent=f"{tool}/{__version__}")
        graph = GraphClient(cfg=cfg, http=http)

        ctx = {
            "cfg": cfg,
            "http": http,
            "graph": graph,
            "out": out,
            "audit": audit,
            "env_file": getattr(args, "env_file", ".env"),
            "version": __version__,
        }
        rc = int(args.func(args, ctx) or 0)
        return rc
    except ValidationError as e:
        audit.write("error", {"error_type": type(e).__name__, "error": str(e)})
        _emit_error(out, tool=tool, version=__version__, command_str=command_str, err=e)
        return 1
    except (NotSupportedError, RemoteApiError, ToolError) as e:
        audit.write("error", {"error_type": type(e).__name__, "error": str(e)})
        _emit_error(out, tool=tool, version=__version__, command_str=command_str, err=e)
        return 1
    except Exception as e:  # noqa: BLE001
        audit.write("error", {"error_type": type(e).__name__, "error": str(e)})
        if bool(getattr(args, "debug", False)):
            raise
        if _argv_wants_json(argv):
            _emit_error(out, tool=tool, version=__version__, command_str=command_str, err=e)
        else:
            print(f"{type(e).__name__}: {e}", file=sys.stderr)
            traceback.print_exc()
        return 1
    finally:
        audit.close()
