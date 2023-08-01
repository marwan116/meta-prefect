"""Deployable flow builder interface."""
from abc import ABC

from prefect.flows import Flow, P, R

from .flow import DeployableFlow


class DeploymentRecipeInterface(ABC):
    """Interface for a deployable flow builder."""

    def __call__(self, flow: Flow[P, R]) -> DeployableFlow[P, R]:
        """Build a deployable flow from a Prefect flow."""
        raise NotImplementedError
