"""A sample local run deployment recipe."""
import os
from typing import Optional

from prefect.client.schemas.schedules import RRuleSchedule
from prefect.flows import Flow, P, R
from pydantic import BaseModel, Field

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
from meta_prefect.implementations.builders.scheduling.env_based_activator import (
    schedule_activator_if_prod,
)
from meta_prefect.implementations.builders.scheduling.federal import (
    federal_holiday_schedule_updater,
)
from meta_prefect.implementations.builders.tags.env_split import env_split_tag_injector
from meta_prefect.implementations.builders.versioning.simple_increment import (
    simple_increment_versioning,
)
from meta_prefect.interface.flow import DeployableFlow
from meta_prefect.interface.recipe import DeploymentRecipeInterface

from .registry import recipes


@recipes.register
class local_run_deployer(BaseModel, DeploymentRecipeInterface):
    name: str = Field(
        description="The name of the deployment.",
    )
    env: str = Field(
        env="META_PREFECT__ENV",
        default=os.environ.get("META_PREFECT__ENV", "dev"),
        description="The environment to deploy to.",
    )
    schedule: Optional[RRuleSchedule] = Field(
        None,
        description="The schedule to deploy the flow with.",
    )
    unique: bool = Field(
        False,
        description="Whether to deploy the flow with a concurrency limiter of 1.",
    )

    def __call__(self, flow: Flow[P, R]) -> "DeployableFlow[P, R]":
        return (
            DeployableFlow.from_prefect_flow(flow)
            .pipe(entrypoint_resolver())
            .pipe(path_resolver())
            .pipe(env_split_namer(name=self.name, env=self.env))
            .pipe(env_split_tag_injector(env=self.env))
            .pipe(local_run_provisioner(env=self.env))
            .pipe(simple_increment_versioning())
            .pipe(federal_holiday_schedule_updater(schedule=self.schedule))
            .pipe(schedule_activator_if_prod(env=self.env))
            .pipe(concurrency_limiter(concurrency_limit=1 if self.unique else None))
        )
