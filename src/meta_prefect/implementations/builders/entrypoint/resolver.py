"""Entrypoint resolver."""
from prefect.utilities.asyncutils import sync_compatible
from pydantic import BaseModel

from meta_prefect.interface import (
    DeployableFlow,
    DeployableFlowBuilderInterface,
    Deployment,
)


class entrypoint_resolver(BaseModel, DeployableFlowBuilderInterface):
    """Entrypoint resolver."""

    @sync_compatible
    async def update_deployment(
        self, flow: DeployableFlow, deployment: Deployment
    ) -> Deployment:
        """Update the deployment."""
        # does changing the name in the flow decorator call impact the entrypoint ?
        deployment.entrypoint = f"{flow.__module__}:{flow.fn.__name__}"

        return deployment
