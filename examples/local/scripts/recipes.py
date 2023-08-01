"""A simple local flow."""
import os
from typing import Callable, Optional

from meta_prefect.implementations.builders.concurrency.limiter import (
    concurrency_limiter,
)
from meta_prefect.implementations.builders.entrypoint.resolver import (
    entrypoint_resolver,
)
from meta_prefect.implementations.builders.infra.local_run import local_run_provisioner
from meta_prefect.implementations.builders.naming.env_based_naming import (
    env_split_namer,
)
from meta_prefect.implementations.builders.path.resolver import path_resolver
from meta_prefect.implementations.builders.scheduling.federal import (
    federal_holiday_schedule_updater,
)
from meta_prefect.implementations.builders.tags.env_split import env_split_tag_injector
from meta_prefect.implementations.builders.versioning.simple_increment import (
    simple_increment_versioning,
)
from meta_prefect.interface.flow import DeployableFlow
from prefect.flows import Flow, P, R
from prefect.server.schemas.schedules import RRuleSchedule


def local_flow_deployer(
    name: str,
    env: Optional[str] = None,
    schedule: Optional[RRuleSchedule] = None,
    unique: bool = False,
) -> Callable[[Flow[P, R]], "DeployableFlow[P, R]"]:
    def from_flow(flow: Flow[P, R]) -> "DeployableFlow[P, R]":
        if env is not None:
            env_to_use = env
        else:
            env_to_use = os.environ.get("META_PREFECT__ENV", "dev")

        return (
            DeployableFlow.from_prefect_flow(flow)
            .pipe(entrypoint_resolver())
            .pipe(path_resolver())
            .pipe(env_split_namer(name=name, env=env_to_use))
            .pipe(env_split_tag_injector(env=env_to_use))
            .pipe(local_run_provisioner(env=env_to_use))
            .pipe(simple_increment_versioning())
            .pipe(federal_holiday_schedule_updater(schedule=schedule))
            .pipe(concurrency_limiter(concurrency_limit=1 if unique else None))
        )

    return from_flow
