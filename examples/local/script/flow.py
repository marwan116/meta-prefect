"""A simple flow."""
import os

import prefect
from prefect.flows import flow


@flow
def add_two_numbers_flow(x: int, y: int) -> int:
    """Add two numbers."""
    logger = prefect.get_run_logger()
    env = os.environ.get("META_PREFECT__ENV")
    logger.info(f"Running add_two_numbers_flow in {env=}")
    out = x + y
    logger.info(f"{out=}")
    return out
