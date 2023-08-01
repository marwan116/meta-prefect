"""Work pool implementation."""
from logging import getLogger
from typing import Any, Dict, Optional

from prefect import get_client
from prefect.client.schemas.actions import WorkPoolCreate
from prefect.client.schemas.objects import WorkPool as ClientWorkPool
from prefect.utilities.asyncutils import sync_compatible
from pydantic import BaseModel, Field

logger = getLogger(__name__)


class WorkPool(BaseModel):
    """Work pool."""

    name: str = Field(
        description="The name of the work pool.",
    )
    description: Optional[str] = Field(
        default=None, description="A description of the work pool."
    )
    type: str = Field(description="The work pool type.")
    base_job_template: Dict[str, Any] = Field(
        default_factory=dict, description="The work pool's base job template."
    )
    is_paused: bool = Field(
        default=False,
        description="Pausing the work pool stops the delivery of all work.",
    )
    concurrency_limit: Optional[int] = Field(
        default=None, description="A concurrency limit for the work pool.", ge=0
    )

    @classmethod
    def from_client_workpool(cls, wp: ClientWorkPool) -> "WorkPool":
        """Create a work pool from a client work pool."""
        return cls.parse_obj(wp.dict())

    @sync_compatible
    async def create(self) -> None:
        wp = WorkPoolCreate(
            name=self.name,
            type=self.type,
            description=self.description,
            base_job_template=self.base_job_template,
            is_paused=self.is_paused,
            concurrency_limit=self.concurrency_limit,
        )
        try:
            async with get_client() as client:
                work_pool = await client.create_work_pool(wp)
                logger.debug(f"Created work pool {work_pool.name}")
        except Exception as e:
            logger.exception(f"Failed to create work pool {self.name}", exc_info=True)
            raise e
