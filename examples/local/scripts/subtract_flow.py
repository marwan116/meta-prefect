"""A simple local flow."""
import os

import prefect
from prefect.flows import flow
from prefect.server.schemas.schedules import RRuleSchedule
from recipes import local_flow_deployer


@flow
def subtract_two_numbers_flow(x: int, y: int) -> int:
    """subtract two numbers."""
    logger = prefect.get_run_logger()
    env = os.environ.get("META_PREFECT__ENV")
    logger.info(f"Running subtract_two_numbers_flow in {env=}")
    out = x - y
    logger.info(f"{out=}")
    return out


my_local_deployable_flow_dev = local_flow_deployer(
    env="dev",
    name="local-run",
    unique=True,
)(subtract_two_numbers_flow)


my_local_deployable_flow_prod = local_flow_deployer(
    env="prod",
    name="local-run",
    schedule=RRuleSchedule(
        rrule="FREQ=DAILY;BYDAY=MO,WE,FR,SA",
        timezone="US/Eastern",
    ),
    unique=True,
)(subtract_two_numbers_flow)
