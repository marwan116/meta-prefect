"""Description resolver."""
from meta_prefect.interface import DeployableFlowBuilderInterface, Deployment
from prefect.utilities.asyncutils import sync_compatible
from pydantic import BaseModel


class description_resolver(BaseModel, DeployableFlowBuilderInterface):
    """description resolver."""

    @sync_compatible
    async def update_deployment(
        self, flow: DeployableFlow, deployment: Deployment
    ) -> Deployment:
        """Update the deployment."""
        # needs access to flow object ?
        deployment.description = "This is a description"
        return deployment
