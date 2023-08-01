"""CLI tool for working with prefect flows and agents."""
import asyncio
import importlib
from collections import defaultdict
from pathlib import Path
from typing import DefaultDict, List, Tuple

import yaml
from prefect.cli.root import app

FlowNameStr = str
app.registered_groups = []
app.registered_commands = []

# from rich import console

# app.console = console
# app.console.print = print


async def _deploy(
    path: str,
    dry_run: bool,
) -> None:
    from prefect.flows import Flow

    from meta_prefect.implementations.project import ProjectSpec
    from meta_prefect.implementations.recipes import recipes
    from meta_prefect.interface import DeployableFlow, Deployment

    meta_prefect_yaml_path = Path(path) / "meta_prefect.yaml"
    if meta_prefect_yaml_path.exists():
        with open(meta_prefect_yaml_path, "r") as f:
            contents = yaml.safe_load(f)
        project_spec = ProjectSpec.parse_obj(contents)
    else:
        project_spec = ProjectSpec(deployments={})

    # find the deployable flows, or build them from the yaml file
    deployable_flows_map: DefaultDict[FlowNameStr, List[DeployableFlow]] = defaultdict(
        list
    )
    for script_path in Path(path).rglob("**/*.py"):
        module_name = script_path.name
        module_path = script_path.resolve().as_posix()

        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None:
            raise ValueError(f"Could not build spec for {module_path}")

        loader = spec.loader
        if loader is None:
            raise ValueError(f"Could not build loader from spec {spec}")

        module = importlib.util.module_from_spec(spec)
        if module is None:
            raise ValueError(f"Could not build module from spec {spec}")

        loader.exec_module(module)

        for attr in dir(module):
            obj = getattr(module, attr)

            if isinstance(obj, DeployableFlow):
                deployable_flows_map[obj.name].append(obj)

            elif isinstance(obj, Flow):
                if obj.name in project_spec.deployments:
                    for deployment_spec in project_spec.deployments[obj.name]:
                        recipe_cls = recipes[deployment_spec.recipe]
                        recipe_obj = recipe_cls.parse_obj(deployment_spec.variables)
                        deployable_flow = recipe_obj(obj)
                        deployable_flows_map[deployable_flow.name].append(
                            deployable_flow
                        )

    # for flow_name, deployable_flows in deployable_flows_map.items():
    #     app.console.print(
    #         f"Performing pre-deployment updates for {flow_name=}...",
    #     )
    #     if dry_run:
    #         app.console.print(
    #             f"Would have performed pre-deployment updates for {flow_name=}.",
    #         )
    #     else:
    #         for deployable_flow in deployable_flows:
    #             await deployable_flow.pre_deployment_update()
    pre_deployment_actions = {
        action
        for deployable_flows in deployable_flows_map.values()
        for action in deployable_flow.pre_deployment_actions
    }
    for action in pre_deployment_actions:
        app.console.print(f"Running {action}...")
        await action.run()

    deployments_map: DefaultDict[
        FlowNameStr, List[Tuple[DeployableFlow, Deployment]]
    ] = defaultdict(list)
    for flow_name, deployable_flows in deployable_flows_map.items():
        app.console.print(
            f"Building deployments for {flow_name=}...",
        )
        if dry_run:
            app.console.print(
                f"Would have built and deployed flow {flow_name}.",
            )
        else:
            for deployable_flow in deployable_flows:
                deployment = await deployable_flow.build_deployment()
                deployments_map[flow_name].append((deployable_flow, deployment))
                app.console.print(f"Applying {deployment.name} for flow {flow_name}...")
                await deployment.apply(upload=True)

    for flow_name, deployments_pair in deployments_map.items():
        app.console.print(
            f"Performing post-deployment update for {flow_name}...",
        )
        if dry_run:
            app.console.print(
                f"Would have performed post-deployment update for {flow_name}."
            )
        else:
            for deployable_flow, deployment in deployments_pair:
                app.console.print(
                    f"Running post-deployment update for {deployment.name} for "
                    f"flow {deployable_flow.name}...",
                )
                await deployable_flow.post_deployment_update(deployment)


@app.command()
def deploy(
    path: str = ".",
    dry_run: bool = False,
) -> None:
    """Deploy prefect flows to prefect cloud.

    Args:
        path: the path to a directory or file containing the prefect flow(s).
            If not specified, the current working directory is used.
        dry_run: if True, pre, post, and deployment steps are not run.
    """
    asyncio.run(_deploy(path, dry_run))


if __name__ == "__main__":
    app()
    # deploy(path="examples/local/script/")
