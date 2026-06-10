from __future__ import annotations

import argparse
import re
import unittest
from pathlib import Path

import google.ads.googleads.v22.services.services as svc_pkg

from google_ads_api_tool.cli import build_parser
from google_ads_api_tool.rpc_v22_registry import RPC_METHODS_V22


_CAMEL_BOUNDARY_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")


def _camel_to_kebab(name: str) -> str:
    parts = _CAMEL_BOUNDARY_RE.split(name.strip())
    return "-".join(p.lower() for p in parts if p)


def _read_surface(path: Path) -> list[str]:
    lines: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        lines.append(s)
    return lines


class TestRpcSurfaceCoverage(unittest.TestCase):
    def test_installed_google_ads_surface_matches_registry(self) -> None:
        base = Path(svc_pkg.__file__).parent
        found: set[str] = set()
        for child in sorted(base.iterdir()):
            if not child.is_dir():
                continue
            grpc_py = child / "transports" / "grpc.py"
            if not grpc_py.exists():
                continue
            for raw in grpc_py.read_text(encoding="utf-8").splitlines():
                m = re.search(
                    r"/google\.ads\.googleads\.v22\.services\.(?P<svc>[^/]+)/(?P<meth>[A-Za-z0-9_]+)",
                    raw,
                )
                if not m:
                    continue
                svc = m.group("svc").split(".")[-1]
                meth = m.group("meth")
                found.add(f"{svc}.{meth}")

        registry = sorted({f"{s.service}.{s.method}" for s in RPC_METHODS_V22})
        self.assertEqual(sorted(found), registry)

    def test_snapshots_match_registry(self) -> None:
        base = Path(__file__).resolve().parent.parent / "docs"
        official = _read_surface(base / "official_rpc_surface_v22_2026-03-01.txt")
        client = _read_surface(base / "client_rpc_surface_v22_2026-03-01.txt")
        cli = _read_surface(base / "cli_rpc_surface_v22_2026-03-01.txt")

        registry = sorted({f"{s.service}.{s.method}" for s in RPC_METHODS_V22})

        self.assertEqual(official, registry)
        self.assertEqual(client, registry)
        self.assertEqual(cli, registry)

    def test_every_rpc_method_is_argparse_registered(self) -> None:
        parser = build_parser()
        for spec in RPC_METHODS_V22:
            service_cmd = _camel_to_kebab(spec.service)
            method_cmd = _camel_to_kebab(spec.method)
            args = parser.parse_args([service_cmd, method_cmd, "--in", "request.json"])
            self.assertEqual(args.rpc_method_spec.service, spec.service)
            self.assertEqual(args.rpc_method_spec.method, spec.method)

    def test_forbidden_generic_bridge_commands_absent(self) -> None:
        parser = build_parser()
        sub = None
        for act in parser._actions:  # noqa: SLF001 (argparse internals)
            if isinstance(act, argparse._SubParsersAction):
                sub = act
                break
        self.assertIsNotNone(sub)
        top_level = set(sub.choices.keys())  # type: ignore[union-attr]
        for forbidden in {"rpc", "call", "invoke", "raw", "bridge"}:
            self.assertNotIn(forbidden, top_level)
