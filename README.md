# Meta-Prefect

## Motivation

Given most folks on a team are not prefect experts, meta-prefect aims to enable the experts to build abstractions to drastically simplify the prefect experience for the rest of the team. 

## How to setup

Using pip:

```bash
pip install meta_prefect
```

## Quickstart

We will walk-through a sample usage and implementation of a local flow deployer.

To deploy a flow locally with just prefect a user needs to:
- create a local worker
- create a local work pool
- deploy the flow with the appropriate metadata (infrastructure, storage, tags, versioning, etc)

In meta-prefect, we can simplify this by using a custom deployer `local_deployer` that implements the `FlowBuilderInterface` class.

See `examples/local/my_local_flow.py`` for reference.
```python
from meta_prefect.implementations.deployer import local_deployer

local_flow = local_deployer()(flow)

@local_flow
def my_flow(x: int, y: int) -> int:
    """Add two numbers x and y."""
    return x + y
```

Note that local_flow can be defined once by the experts and used by the rest of the team to deploy flows locally.

When the flow is deployed, the deployer will:
- create a local worker
- create a local work pool
- deploy the flow with the appropriate metadata:
    - a local flow storage with the appropriate endpoint
    - tags will be picked up from `META_PREFECT__TAGS` environment variable
    - versioning will be picked up from `META_PREFECT__VERSION` environment variable

With meta-prefect, the expert can implement deployment builders that can be used by the rest of 
the team to deploy flows to a variety of infrastructures by simply running

```bash
export META_PREFECT__TAGS="my-tag"
export META_PREFECT__VERSION="my-version"
meta-prefect deploy my_flow
```

The way local_deployer works is by wrapping the flow with a decorator that implements the `FlowBuilderInterface` class.

```python
from meta_prefect.interfaces.flow_builder_interface import FlowBuilderInterface
from meta_prefect.interfaces.components import WorkerPool, Worker

class local_deployer(FlowBuilderInterface):
    def __init__(self):
        pass
    
    @property
    def requires(self) -> Set[str]:
        return set(
            WorkerPool(),
            Worker(),
        )
    
    def update_deployment(self, deployment: Deployment) -> Deployment:
        deployment.flow.storage = Local()
        deployment.flow.run_config = LocalRun()
        deployment.flow.environment = LocalEnvironment()
        deployment.flow.executor = LocalDaskExecutor()
        deployment.flow.metadata = LocalMetadata()
        return deployment
```

### Limitations

meta-prefect currently has the following limitations:

- not all deploymet components have been implemented (contributions are welcome!) - most notably:
    - automations
    - dask executors
- a user can't immediately create multiple deployments from a given flow. Instead the user needs to clone the flow (using prefect flow.with_options is recommended) so that
the flow can be deployed multiple times with different metadata. 


## How to use

Create your custom deployer by implementing the `FlowBuilderInterface` class, or use one of the implementations provided by the library.

For example to deploy flows:
- to an EKS cluster
- persist results to s3
- use a dask-kubernetes task runner
- infer deployment metadata from the flow

you would write a snippet like this

```python
from meta_prefect.implementations.infra import eks as kubernetes
from meta_prefect.implementations.task_runner import dask_k8s as dask
from meta_prefect.implementations.metadata import versioneer, tags_resolver 
from meta_prefect.implementations.filesystem import S3Filesystem

flow = versioneer()(tags_resolver())(flow)

@kubernetes(
    cpu=0.8,
    memory=1.5,
)
@dask(
    num_workers=5
)
@flow(
    result_storage=S3Filesystem(
        type="s3",
        bucket="my-bucket",
        path="my-path",
    )
)
def complex_eks_dask_flow(x: int, y: int) -> int:
    """Add two numbers x and y."""
```
