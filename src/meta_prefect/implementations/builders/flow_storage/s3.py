"""S3 Flow Storage Implementation."""
from prefect.filesystems import S3
from prefect.utilities.asyncutils import sync_compatible
from pydantic import BaseModel

from meta_prefect.interface import DeployableFlowBuilderInterface, Deployment


class s3(BaseModel, DeployableFlowBuilderInterface):
    """S3 infrastructure builder."""

    bucket: str
    key: str

    # @sync_compatible
    # async def update_pre_deployment(self, flow) -> None:
    #     """Update pre deployment."""

    @sync_compatible
    async def update_deployment(
        self, flow: DeployableFlow, deployment: Deployment
    ) -> Deployment:
        """Update deployment."""
        deployment.storage = S3(bucket_path=f"{self.bucket}/{self.key}")
        deployment.path = None
        return deployment
