import prefect
from prefect import flow

from etl_machine.recipes import local_flow_deployer


@flow
def load_data() -> None:
    """Load data from a source."""
    logger = prefect.get_run_logger()
    logger.info("Loading data")


local_run = local_flow_deployer(name="local-run")(load_data)
