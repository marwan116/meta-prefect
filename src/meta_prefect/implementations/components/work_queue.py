"""Work queue implementation."""
from logging import getLogger
from typing import Optional

from prefect import get_client
from prefect.client.schemas.objects import WorkQueue as ClientWorkQueue
from prefect.utilities.asyncutils import sync_compatible
from pydantic import BaseModel, Field

logger = getLogger(__name__)


class WorkQueue(BaseModel):
    """Work queue."""

    name: str = Field(default=..., description="The name of the work queue.")
    description: Optional[str] = Field(
        default="", description="An optional description for the work queue."
    )
    is_paused: bool = Field(
        default=False, description="Whether or not the work queue is paused."
    )
    concurrency_limit: Optional[int] = Field(
        default=None,
        description="An optional concurrency limit for the work queue.",
        ge=0,
    )
    priority: int = Field(
        default=1,
        ge=1,
        description=(
            "The queue's priority. Lower values are higher priority (1 is the highest)."
        ),
    )
    work_pool_name: Optional[str] = Field(default=None)

    @classmethod
    def from_client_workqueue(cls, wp: ClientWorkQueue) -> "WorkQueue":
        """Create a work pool from a client work pool."""
        return cls.parse_obj(wp.dict())

    @sync_compatible
    async def create(self) -> None:
        try:
            async with get_client() as client:
                work_queue = await client.create_work_queue(
                    name=self.name,
                    description=self.description,
                    is_paused=self.is_paused,
                    concurrency_limit=self.concurrency_limit,
                    priority=self.priority,
                    work_pool_name=self.work_pool_name,
                )
                logger.debug(f"Created work queue {work_queue.name}")
        except Exception as e:
            logger.exception(f"Failed to create work queue {self.name}", exc_info=True)
            raise e
