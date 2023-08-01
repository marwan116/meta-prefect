"""A tag updater that will include environment split info."""
from meta_prefect.interface import DeployableFlowBuilderInterface, Deployment
from meta_prefect.interface.flow import DeployableFlow
from prefect.utilities.asyncutils import sync_compatible
from pydantic import BaseModel, Field


class env_split_namer(BaseModel, DeployableFlowBuilderInterface):
    """Environment split-based naming."""

    name: str = Field(
        ...,
        description="The name of the deployment.",
    )

    env: str = Field(
        ...,
        env="META_PREFECT__ENV",
        description="The environment split to reference in the deployment name.",
    )

    @sync_compatible
    async def update_deployment(
        self, flow: DeployableFlow, deployment: Deployment
    ) -> Deployment:
        """Update the deployment."""
        deployment.name = f"{self.name}-{self.env}"
        return deployment
