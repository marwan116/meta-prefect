"""Env-based schedule activator."""
from meta_prefect.interface.builder import DeployableFlowBuilderInterface
from meta_prefect.interface.deployment import Deployment
from meta_prefect.interface.flow import DeployableFlow
from prefect.utilities.asyncutils import sync_compatible
from pydantic import BaseModel, Field


class schedule_activator_if_prod(BaseModel, DeployableFlowBuilderInterface):
    """Schedule activator if prod."""

    env: str = Field(
        ...,
        env="META_PREFECT__ENV",
        description="The environment split to deploy to.",
    )

    @sync_compatible
    async def update_deployment(
        self, flow: DeployableFlow, deployment: Deployment
    ) -> Deployment:
        """Update the deployment."""
        deployment.is_schedule_active = self.env == "prod"
        return deployment
