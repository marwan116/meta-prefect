"""A deployment versioneer that relies on the underlying flow package."""
from prefect.utilities.asyncutils import sync_compatible
from pydantic import BaseModel, Field

from meta_prefect.interface import DeployableFlowBuilderInterface, Deployment
from meta_prefect.interface.flow import DeployableFlow


class pacakge_based_versioning(BaseModel, DeployableFlowBuilderInterface):
    """Package based versioning."""

    pacakge_name: str = Field(
        ...,
        env="META_PREFECT__PACKAGE_NAME",
        description="The name of the package to use for versioning.",
    )

    @property
    def version(self) -> str:
        """Get the version of the package."""
        import importlib.metadata

        return importlib.metadata.version(self.pacakge_name)

    @sync_compatible
    async def update_deployment(
        self, flow: DeployableFlow, deployment: Deployment
    ) -> Deployment:
        """Update the deployment."""
        deployment.version = self.version
        return deployment
