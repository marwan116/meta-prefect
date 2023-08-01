"""Deployable flow and builder interface."""
from abc import ABC, abstractmethod

from prefect.flows import Flow, P, R
from prefect.utilities.asyncutils import sync_compatible

from .deployment import Deployment
from .flow import DeployableFlow

class DeployableFlowBuilderInterface(ABC):
    """Deployable-deployer mypy-friendly stub."""

    @sync_compatible
    async def update_pre_deployment(
        self, flow: DeployableFlow[P, R]
    ) -> DeployableFlow[P, R]: ...
    @abstractmethod
    @sync_compatible
    async def update_deployment(
        self, flow: DeployableFlow, deployment: Deployment
    ) -> Deployment: ...
    @sync_compatible
    async def update_post_deployment(
        self, flow: DeployableFlow, deployment: Deployment
    ) -> None: ...
    def __call__(self, flow: Flow[P, R]) -> DeployableFlow[P, R]: ...
