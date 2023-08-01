from typing import Any, Dict

from prefect.deployments import Deployment as _Deployment  # type: ignore


class Deployment(_Deployment):
    """Prefect deployment with additional properties."""

    additional_properties: Dict[str, Any] = {}
