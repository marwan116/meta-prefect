"""Deployable flow interface."""
from typing import Any, Callable, List, Tuple, cast

from prefect.flows import Flow, P, R
from prefect.utilities.asyncutils import sync_compatible
from prefect.utilities.callables import parameter_schema

from .builder import DeployableFlowBuilderInterface
from .deployment import Deployment


def _get_wrapped_init() -> Callable[..., None]:
    """Flow.__init__ is wrapped by PrefectObjectRegistry.register_instances."""
    wrapped_init = [
        cell
        for cell in Flow.__init__.__closure__ or tuple()
        if cell.cell_contents.__name__ == "__init__"
    ]
    if len(wrapped_init) != 1:
        raise ValueError("Could not find wrapped init")
    return cast(Callable[..., None], wrapped_init[0].cell_contents)


def get_arg_names_from_wrapped_init() -> Tuple[str, ...]:
    wrapped_init = _get_wrapped_init()
    args = wrapped_init.__code__.co_varnames
    args_wo_self = args[1:]
    return args_wo_self


class DeployableFlow(Flow[P, R]):
    """DeployableFlow is a prefect flow that can deploy itself."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        __super__init__ = _get_wrapped_init()
        __super__init__(self, *args, **kwargs)

        if not hasattr(self, "deployment_builders"):
            self._deployment_builders: List[DeployableFlowBuilderInterface] = []

    @classmethod
    def from_prefect_flow(cls, flow: Flow[P, R]) -> "DeployableFlow[P, R]":
        params = {
            k: v
            for k, v in vars(flow).items()
            if k in get_arg_names_from_wrapped_init()
        }
        return cls(**params)

    @property
    def deployment_builders(self) -> List[DeployableFlowBuilderInterface]:
        return self._deployment_builders

    @deployment_builders.setter
    def deployment_builders(
        self, deployment_builders: List[DeployableFlowBuilderInterface]
    ) -> None:
        if not isinstance(deployment_builders, list):
            raise TypeError(f"Expected list got {type(deployment_builders)}")
        for builder in deployment_builders:
            if not isinstance(builder, DeployableFlowBuilderInterface):
                raise TypeError(
                    f"Expected DeployableFlowBuilderInterface got {type(builder)}"
                )
        self._deployment_builders = deployment_builders

    @sync_compatible
    async def pre_deployment_update(self) -> None:
        """Perform pre-deployment updates."""
        for deployment_builder in self.deployment_builders:
            await deployment_builder.update_pre_deployment(self)

    @property
    def pre_deployment_actions(self):
        """Pre deployment actions."""
        return {
            action
            for deployment_builder in self.deployment_builders
            for action in deployment_builder.pre_deployment_actions
        }

    @sync_compatible
    async def build_deployment(self) -> Deployment:
        """Build a deployment."""
        deployment = Deployment(name=self.name, work_queue_name=None, storage=None)
        deployment.flow_name = self.name
        deployment.parameter_openapi_schema = parameter_schema(self)
        for deployment_builder in self.deployment_builders:
            deployment = await deployment_builder.update_deployment(
                flow=self, deployment=deployment
            )
        return deployment

    @sync_compatible
    async def post_deployment_update(self, deployment: Deployment) -> None:
        """Perform post-deployment updates."""
        for deployment_builder in self.deployment_builders:
            await deployment_builder.update_post_deployment(
                flow=self, deployment=deployment
            )

    def pipe(self, other: DeployableFlowBuilderInterface) -> "DeployableFlow[P, R]":
        """Pipe operator."""
        if not isinstance(other, DeployableFlowBuilderInterface):
            raise TypeError(
                f"Expected DeployableFlowBuilderInterface got {type(other)}"
            )
        return other(self)
