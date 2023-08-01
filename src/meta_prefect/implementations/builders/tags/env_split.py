"""A tag updater that will include environment split info."""
from typing import Any

from meta_prefect.interface import DeployableFlowBuilderInterface, Deployment
from meta_prefect.interface.flow import DeployableFlow
from prefect.utilities.asyncutils import sync_compatible
from pydantic import BaseModel, Field


class env_split_tag_injector(BaseModel, DeployableFlowBuilderInterface):
    """Environment split tag injector."""

    env: str = Field(
        ...,
        env="META_PREFECT__ENV",
        description="The environment split to deploy to.",
    )

    @sync_compatible
    async def update_deployment(
        self, flow: DeployableFlow[Any, Any], deployment: Deployment
    ) -> Deployment:
        """Update the deployment."""
        if deployment.tags:
            deployment.tags = list(set(deployment.tags).union([f"env={self.env}"]))

        else:
            deployment.tags = [f"env={self.env}"]
        return deployment
