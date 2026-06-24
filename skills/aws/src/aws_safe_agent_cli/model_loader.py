from __future__ import annotations

from functools import lru_cache

from botocore.session import get_session


@lru_cache(maxsize=None)
def load_service_model(service_name: str):
    return get_session().get_service_model(service_name)


@lru_cache(maxsize=None)
def load_operation_model(service_name: str, operation_name: str):
    return load_service_model(service_name).operation_model(operation_name)

