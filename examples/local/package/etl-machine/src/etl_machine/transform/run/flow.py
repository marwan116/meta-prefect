import prefect
from prefect import flow

from etl_machine.recipes import local_flow_deployer


@flow
def transform_data() -> None:
    """Transform data from a source."""
    logger = prefect.get_run_logger()
    logger.info("Transforming data")


local_run = local_flow_deployer(name="local-run")(transform_data)
