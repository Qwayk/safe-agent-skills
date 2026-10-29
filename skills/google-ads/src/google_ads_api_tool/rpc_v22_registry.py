"""Compatibility import for callers using the former registry module name.

Requests now use the supported v25 registry; no v22 endpoints are retained.
"""

from .rpc_v25_registry import RPC_METHODS_V25 as RPC_METHODS_V22, RpcMethodSpec
