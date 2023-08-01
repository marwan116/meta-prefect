"""Actions for work queus."""
from typing import FrozenSet, Optional
from uuid import uuid4

from prefect import get_client

from meta_prefect.implementations.components.work_pool import WorkPool
from meta_prefect.implementations.components.work_queue import WorkQueue

from .base import Action
from .work_pool import EnsureLocalProcessWorkPoolCreatedAction


class EnsureWorkQueueCreatedAction(Action):
    """Ensure a work queue is created."""

    concurrency_limit: Optional[int] = None

    requires: FrozenSet["Action"] = frozenset(
        {EnsureLocalProcessWorkPoolCreatedAction()}
    )

    def __repr__(self) -> str:
        return (
            f"EnsureWorkQueueCreatedAction(concurrency_limit={self.concurrency_limit})"
        )

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
                    wq = work_queue
                    break
            else:
                wq = WorkQueue(
                    name=f"work-queue-{str(uuid4())[:8]}",
                    work_pool_name=work_pool.name,
                    concurrency_limit=self.concurrency_limit,
                )
                await wq.create()
        return wq

    async def _run(self) -> WorkQueue:
        work_pool_action = next(
            action
            for action in self.requires
            if isinstance(action, EnsureLocalProcessWorkPoolCreatedAction)
        )
        work_pool = await work_pool_action.run()
        return await self._ensure_work_queue_created(work_pool)
