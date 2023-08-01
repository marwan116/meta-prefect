"""Actions for work pools."""
from typing import List
from uuid import uuid4

from prefect import get_client
from prefect.workers.process import ProcessJobConfiguration

from meta_prefect.implementations.components.work_pool import WorkPool

from .base import Action


class EnsureLocalProcessWorkPoolCreatedAction(Action):
    """Ensure a local process work pool is created."""

    def __repr__(self) -> str:
        return "EnsureLocalProcessWorkPoolCreatedAction()"

    async def _get_existing_work_pools(self) -> List[WorkPool]:
        async with get_client() as client:
            available_workpools = await client.read_work_pools()
        return [WorkPool.from_client_workpool(wp) for wp in available_workpools]

    async def _run(self) -> WorkPool:
        for work_pool in await self._get_existing_work_pools():
            if work_pool.type == "process":
                job_config = work_pool.base_job_template["job_configuration"]
                if job_config["env"]["META_PREFECT__ENV"] == "{{env}}":
                    break
        else:
            work_pool = WorkPool(
                name=f"local-process-work-pool-{str(uuid4())[:8]}",
                type="process",
                base_job_template={
                    "job_configuration": {
                        k: v
                        for k, v in ProcessJobConfiguration(
                            env={"META_PREFECT__ENV": "{{env}}"}
                        )
                        .dict()
                        .items()
                        if v is not None
                    },
                    "variables": {
                        "type": "object",
                        "properties": {
                            "env": {
                                "type": "string",
                                "default": "dev",
                            }
                        },
                    },
                },
            )
            work_pool.create()
        return work_pool
