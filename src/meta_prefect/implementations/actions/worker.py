"""Actions for workers."""
from typing import FrozenSet

from pendulum import duration
from prefect import get_client
from prefect._internal.schemas.fields import DateTimeTZ
from prefect.client.schemas.filters import WorkerFilter, WorkerFilterLastHeartbeatTime
from pydantic import Field

from meta_prefect.implementations.components.work_pool import WorkPool
from meta_prefect.implementations.components.worker import ProcessWorker
from meta_prefect.implementations.utils import get_machine_id

from .base import Action
from .work_pool import EnsureLocalProcessWorkPoolCreatedAction


class EnsureWorkerCreatedAction(Action):
    """Ensure a worker is created."""

    requires: FrozenSet["Action"] = frozenset(
        {EnsureLocalProcessWorkPoolCreatedAction()}
    )

    machine_id: str = Field(
        default_factory=get_machine_id,
        description="The machine ID of the worker to create.",
    )

    def __repr__(self) -> str:
        return f"EnsureWorkerCreatedAction(machine_id={self.machine_id})"

    async def _ensure_local_worker_created(self, work_pool: WorkPool) -> ProcessWorker:
        async with get_client() as client:
            workers = [
                ProcessWorker.from_client_worker(w, work_pool.name)
                for w in await client.read_workers_for_work_pool(
                    work_pool_name=work_pool.name,
                    worker_filter=WorkerFilter(
                        last_heartbeat_time=WorkerFilterLastHeartbeatTime(
                            after_=DateTimeTZ.now() - duration(minutes=10)
                        )
                    ),
                )
            ]

            for worker in workers:
                if self.machine_id in worker.name:
                    break
            else:
                worker = ProcessWorker(work_pool_name=work_pool.name)
                await worker.create()
        return worker

    async def _run(self) -> ProcessWorker:
        work_pool_action = next(
            action
            for action in self.requires
            if isinstance(action, EnsureLocalProcessWorkPoolCreatedAction)
        )
        work_pool = await work_pool_action.run()
        return await self._ensure_local_worker_created(work_pool)
