"""A deployment versioneer that versions by incrementing the existing version."""
from prefect import get_client
from prefect.client.schemas.filters import (
    DeploymentFilter,
    DeploymentFilterName,
    DeploymentFilterTags,
    FlowFilter,
    FlowFilterName,
    FlowFilterTags,
)
from prefect.client.schemas.sorting import DeploymentSort
from prefect.utilities.asyncutils import sync_compatible
from pydantic import BaseModel

from meta_prefect.interface import DeployableFlowBuilderInterface, Deployment
from meta_prefect.interface.flow import DeployableFlow


class simple_increment_versioning(BaseModel, DeployableFlowBuilderInterface):
    """Simple increment versioning."""

    async def _get_existing_version(
        self, flow: DeployableFlow, deployment: Deployment
    ) -> int:
        """Get the existing version."""
        async with get_client() as client:
            latest_deployment = await client.read_deployments(
                flow_filter=FlowFilter(
                    name=FlowFilterName(any=[flow.name]),
                ),
                deployment_filter=DeploymentFilter(
                    name=DeploymentFilterName(any_=[deployment.name]),
                    tags=DeploymentFilterTags(all_=deployment.tags),
                ),
                limit=1,
                sort=DeploymentSort.UPDATED_DESC,
            )

        if not latest_deployment:
            return 0

        version = latest_deployment[0].version

        try:
            return int(version)

        except ValueError as e:
            raise ValueError(
                f"Existing version {version} is not an integer. "
                "Please use a different versioning strategy."
            ) from e

    @sync_compatible
    async def update_deployment(
        self, flow: DeployableFlow, deployment: Deployment
    ) -> Deployment:
        """Update the deployment."""
        existing_version = await self._get_existing_version(flow, deployment)
        new_version = existing_version + 1
        deployment.version = str(new_version)
        return deployment
