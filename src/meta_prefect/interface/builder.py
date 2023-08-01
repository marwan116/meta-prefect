# type: ignore
"""Deployable flow builder interface."""
from abc import ABC, abstractmethod

from prefect.utilities.asyncutils import sync_compatible


class DeployableFlowBuilderInterface(ABC):
    """Interface for a deployable flow builder."""

    @property
    def pre_deployment_actions(self):
        return set()

    @sync_compatible
    async def update_pre_deployment(self, flow):
        return flow

    @abstractmethod
    @sync_compatible
    async def update_deployment(self, flow, deployment):
        ...

    @sync_compatible
    async def update_post_deployment(self, flow, deployment):
        return

    def __call__(self, flow):
        flow.deployment_builders.append(self)
        return flow
