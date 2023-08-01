"""Path resolver."""
from pathlib import Path

from meta_prefect.interface import DeployableFlowBuilderInterface, Deployment
from meta_prefect.interface.flow import DeployableFlow
from prefect.utilities.asyncutils import sync_compatible
from pydantic import BaseModel


class path_resolver(BaseModel, DeployableFlowBuilderInterface):
    """path resolver."""

    @sync_compatible
    async def update_deployment(
        self, flow: DeployableFlow, deployment: Deployment
    ) -> Deployment:
        """Update the deployment."""
        is_docker_based = hasattr(deployment.infrastructure, "image")

        if not deployment.storage and not is_docker_based and not deployment.path:
            deployment.path = str(Path(".").absolute())
        elif not deployment.storage and is_docker_based:
            # only update if a path is not already set
            if not deployment.path:
                deployment.path = "/opt/prefect/flows"

        deployment.path = Path.cwd().resolve().as_posix()

        return deployment
