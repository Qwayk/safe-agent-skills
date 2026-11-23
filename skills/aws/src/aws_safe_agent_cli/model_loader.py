from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import botocore
from botocore.loaders import Loader
from botocore.session import Session


def pinned_session() -> Session:
    session = Session()
    loader = Loader(
        extra_search_paths=[str(Path(botocore.__file__).parent / "data")],
        include_default_search_paths=False,
        include_default_extras=False,
    )
    session.register_component("data_loader", loader)
    return session


@lru_cache(maxsize=None)
def load_service_model(service_name: str):
    return pinned_session().get_service_model(service_name)


@lru_cache(maxsize=None)
def load_operation_model(service_name: str, operation_name: str):
    return load_service_model(service_name).operation_model(operation_name)

