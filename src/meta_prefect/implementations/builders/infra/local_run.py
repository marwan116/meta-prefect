"""A local run provisioner."""
from typing import List, Set
from uuid import uuid4

from meta_prefect.implementations.actions.base import Action
from meta_prefect.implementations.actions.work_pool import (
    EnsureLocalProcessWorkPoolCreatedAction,
)
from meta_prefect.implementations.actions.worker import EnsureWorkerCreatedAction
from meta_prefect.implementations.components.work_pool import WorkPool
from meta_prefect.implementations.components.worker import ProcessWorker
from meta_prefect.implementations.utils import get_machine_id
from meta_prefect.interface import (
    DeployableFlow,
    DeployableFlowBuilderInterface,
    Deployment,
)
from pendulum import duration
from prefect import get_client
from prefect._internal.schemas.fields import DateTimeTZ
from prefect.client.schemas.filters import WorkerFilter, WorkerFilterLastHeartbeatTime
from prefect.flows import P, R
from prefect.utilities.asyncutils import sync_compatible
from prefect.workers.process import ProcessJobConfiguration
from pydantic import BaseModel, Field, PrivateAttr


class local_run_provisioner(BaseModel, DeployableFlowBuilderInterface):
    """Local run provisioner."""

    env: str = Field(
        ...,
        env="META_PREFECT__ENV",
        description="The environment split to reference in the deployment name.",
    )

    _work_pool: WorkPool = PrivateAttr(None)

    async def _get_existing_work_pools(self) -> List[WorkPool]:
        """Get the existing work pools."""
        async with get_client() as client:
            available_workpools = await client.read_work_pools()
        return [WorkPool.from_client_workpool(wp) for wp in available_workpools]

    async def _ensure_work_pool_created(self) -> WorkPool:
        # ProcessJobConfiguration
        for work_pool in await self._get_existing_work_pools():
            if work_pool.type == "process":
                self._work_pool = work_pool
                break
        else:
            self._work_pool = WorkPool(
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
                                "default": self.env,
                            }
                        },
                    },
                },
            )
            await self._work_pool.create()
        return work_pool

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
                if get_machine_id() in worker.name:
                    break
            else:
                worker = ProcessWorker(work_pool_name=self._work_pool.name)
                await worker.create()
        return worker

    @sync_compatible
    async def update_pre_deployment(
        self, flow: DeployableFlow[P, R]
    ) -> DeployableFlow[P, R]:
        work_pool = await self._ensure_work_pool_created()
        await self._ensure_local_worker_created(work_pool)
        return flow

    @property
    def pre_deployment_actions(self) -> Set[Action]:
        create_work_pool = EnsureLocalProcessWorkPoolCreatedAction()
        create_worker = EnsureWorkerCreatedAction()
        return {
            create_work_pool,
            create_worker,
        }

    @sync_compatible
    async def update_deployment(
        self, flow: DeployableFlow, deployment: Deployment
    ) -> Deployment:
        """Update the deployment."""
        work_pool = EnsureLocalProcessWorkPoolCreatedAction().result
        deployment.work_pool_name = work_pool.name
        deployment.infra_overrides.update({"env": self.env})
        return deployment
