"""A deployment builder enforcing a deployment goes to a work queue with set limit."""
from typing import List, Optional, Set
from uuid import uuid4

from prefect import get_client
from prefect.flows import P, R
from prefect.utilities.asyncutils import sync_compatible
from pydantic import BaseModel, PrivateAttr

from meta_prefect.implementations.actions.base import Action
from meta_prefect.implementations.actions.work_pool import (
    EnsureLocalProcessWorkPoolCreatedAction,
)
from meta_prefect.implementations.actions.work_queue import EnsureWorkQueueCreatedAction
from meta_prefect.implementations.components.work_pool import WorkPool
from meta_prefect.implementations.components.work_queue import WorkQueue
from meta_prefect.interface import (
    DeployableFlow,
    DeployableFlowBuilderInterface,
    Deployment,
)


class concurrency_limiter(BaseModel, DeployableFlowBuilderInterface):
    """concurrency limiter."""

    concurrency_limit: Optional[int] = None
    _work_pool: WorkPool = PrivateAttr(None)
    _work_queue: WorkQueue = PrivateAttr(None)

    async def _get_existing_work_pools(self) -> List[WorkPool]:
        """Get the existing work pools."""
        async with get_client() as client:
            available_workpools = [
                WorkPool.from_client_workpool(wp)
                for wp in await client.read_work_pools()
            ]
        return available_workpools

    async def _ensure_work_pool_created(self) -> WorkPool:
        for work_pool in await self._get_existing_work_pools():
            if work_pool.type == "process":
                self._work_pool = work_pool
                break
        else:
            raise ValueError("No process work pool found.")
        return work_pool

    async def _ensure_work_queue_created(self, work_pool: WorkPool) -> WorkQueue:
        async with get_client() as client:
            work_queues = [
                WorkQueue.from_client_workqueue(wq)
                for wq in await client.read_work_queues(
                    work_pool_name=work_pool.name,
                )
            ]

            for work_queue in work_queues:
                if work_queue.concurrency_limit == self.concurrency_limit:
                    self._work_queue = work_queue
                    break
            else:
                wq = WorkQueue(
                    name=f"work-queue-{str(uuid4())[:8]}",
                    work_pool_name=self._work_pool.name,
                    concurrency_limit=self.concurrency_limit,
                )
                await wq.create()
                self._work_queue = wq
        return work_queue

    @sync_compatible
    async def update_pre_deployment(
        self, flow: "DeployableFlow[P, R]"
    ) -> "DeployableFlow[P, R]":
        work_pool = await self._ensure_work_pool_created()
        await self._ensure_work_queue_created(work_pool)
        return flow

    @property
    def pre_deployment_actions(self) -> Set[Action]:
        create_work_pool = EnsureLocalProcessWorkPoolCreatedAction()
        create_work_queue = EnsureWorkQueueCreatedAction()
        return {
            create_work_pool,
            create_work_queue,
        }

    @sync_compatible
    async def update_deployment(
        self, flow: DeployableFlow[P, R], deployment: Deployment
    ) -> Deployment:
        """Update the deployment."""
        work_queue = EnsureWorkQueueCreatedAction().result
        deployment.work_queue_name = work_queue.name
        return deployment
