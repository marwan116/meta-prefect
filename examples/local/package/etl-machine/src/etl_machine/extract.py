import prefect
from prefect import flow

from etl_machine.recipes import local_flow_deployer


@flow
def extract_data() -> None:
    """Extract data from a source."""
    logger = prefect.get_run_logger()
    logger.info("Extracting data")


local_run = local_flow_deployer(name="local-run")(extract_data)
