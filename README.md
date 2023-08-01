# Meta-Prefect

## Motivation

Meta-prefect provides python abstractions to enable engineering teams to enforce opinionated recipes for deploying prefect flows.

The main goals are to:
* **help avoid "negative engineering"** in repeating boilerplate code and configuration when deploying flows
* **drastically simplify** the prefect experience for all folks on an engineering team.
* **provide much more flexibility** by allowing recipes to be composed in code and not via yaml files.

## Requirments

Python 3.8+

**Meta-Prefect** is an extension of [Prefect](https://www.prefect.io/) and requires prefect to be installed.

## Installation

Using pip:

```bash
pip install meta_prefect
```

## Example

### The absolute minimum

* Create a file `flow.py` with:

```python
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
```

* Create a file `meta_prefect.yaml` with:

```yaml
deployments:
  add-two-numbers-flow:
    - recipe: local_run_deployer
      variables:
        name: local-run
        schedule:
          rrule: "FREQ=DAILY;BYDAY=MO,WE,FR,SA"
          timezone: "US/Pacific"
```

### Deploy it

* Run `meta-prefect deploy`

### Let's inspect what happened:

* A prefect flow was registered in prefect cloud:

```bash
$ prefect flow ls          
                                              Flows                                               
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                   ID ┃ Name                 ┃ Created                          ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 6437c45e-1d4e-415b-b7bb-ae1f30c5f0d8 │ add-two-numbers-flow │ 2023-08-08T20:58:31.826573+00:00 │
└──────────────────────────────────────┴──────────────────────┴──────────────────────────────────┘    
```

* A prefect deployment was created:

```bash
$ prefect deployment ls
                                   Deployments                                   
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name                                   ┃ ID                                   ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ add-two-numbers-flow/local-run-dev     │ 1b0c1ab8-3383-4b5c-a9b8-a3aa04bef1bf │
└────────────────────────────────────────┴──────────────────────────────────────┘

$ prefect deployment inspect add-two-numbers-flow/local-run-dev
{
    'id': '1b0c1ab8-3383-4b5c-a9b8-a3aa04bef1bf',
    'created': '2023-08-08T20:58:33.021080+00:00',
    'updated': '2023-08-08T21:31:01.071234+00:00',
    'name': 'local-run-dev',
    'version': '6',
    'description': None,
    'flow_id': '6437c45e-1d4e-415b-b7bb-ae1f30c5f0d8',
    'schedule': {
        'rrule': 
'FREQ=DAILY;BYDAY=MO,WE,FR,SA\nEXDATE:20240115T000000,20240219T000000,20241014T000000,20240101T000000,20240527T000000,2
0240619T000000,20240704T000000,20240902T000000,20241111T000000,20241128T000000,20241225T000000,20230116T000000,20230220
T000000,20231009T000000,20230101T000000,20230102T000000,20230529T000000,20230619T000000,20230704T000000,20230904T000000
,20231111T000000,20231110T000000,20231123T000000,20231225T000000',
        'timezone': 'US/Pacific'
    },
    'is_schedule_active': False,
    'infra_overrides': {'env': 'dev'},
    'parameters': {},
    'tags': ['env=dev'],
    'work_queue_name': 'default',
    'parameter_openapi_schema': {
        'type': 'object',
        'title': 'Parameters',
        'required': ['x', 'y'],
        'properties': {
            'x': {'type': 'integer', 'title': 'x', 'position': 0},
            'y': {'type': 'integer', 'title': 'y', 'position': 1}
        }
    },
    'pull_steps': [],
    'manifest_path': None,
    'storage_document_id': None,
    ...
    'work_pool_name': 'local-process-work-pool-6da5fdd6',
    'infrastructure': {
        'type': 'process',
        'env': {},
        'labels': {},
        'name': None,
        'command': None,
        'stream_output': True,
        'working_dir': None,
        'block_type_slug': 'process'
    },
    'automations': []
}
```

* A prefect work pool was created:

```bash
$ prefect work-pool ls     
                                                  Work Pools                                                   
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓
┃ Name                             ┃ Type          ┃                                   ID ┃ Concurrency Limit ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
│ local-process-work-pool-6da5fdd6 │ process       │ 32f55e3b-4427-4f45-88aa-e20ac2fadc48 │ None              │
└──────────────────────────────────┴───────────────┴──────────────────────────────────────┴───────────────────┘

$ prefect work-pool inspect 'local-process-work-pool-6da5fdd6'
WorkPool(
    id='32f55e3b-4427-4f45-88aa-e20ac2fadc48',
    created=DateTime(2023, 8, 8, 20, 58, 29, 351051, tzinfo=Timezone('+00:00')),
    updated=DateTime(2023, 8, 8, 20, 58, 29, 351552, tzinfo=Timezone('+00:00')),
    name='local-process-work-pool-6da5fdd6',
    type='process',
    base_job_template={
        'variables': {'type': 'object', 'properties': {'env': {'type': 'string', 'default': 'dev'}}},
        'job_configuration': {'env': {'META_PREFECT__ENV': '{{env}}'}, 'labels': {}, 'stream_output': True}
    },
    default_queue_id='c6ec1eb9-f617-4aee-9820-8ff7692c289e'
)
```

* A prefect worker was created:

```bash
$ prefect worker ls
                                                  Workers
┏━━━
┃ Name                             ┃ Type          ┃                                   ID ┃ Labels ┃ Last Heartbeat ┃
┡━━━
```


This will:
- create a work pool
- create a worker
- create a deployment with:
    - a name `local-run-dev` to identify the deployment as a local run in the dev environment
    - a tag `env=dev` to be able to filter deployments by environment
    - a version `1` to be able to track the version of the deployment through an intuitive versioning scheme. This is an auto-incrementing integer that is incremented every time `meta-prefect deploy` is called.
- provide the appropriate entrypoint and path to run the flow

### How it works

The `meta_prefect.yaml` file defines a recipe and a flow.

The recipe is a set of instructions that can be used to deploy a flow.

This recipe is called `local_run_deployer` and is defined as a sample implementation. 

Here is the implementation of the `local_run_deployer` recipe:

```python



We will walk-through a sample usage and implementation of a local flow deployer.

To deploy a flow to prefect cloud which will be executed locally a prefect user needs to:
- create a work pool
- create a worker
- deploy the flow with the appropriate metadata (tags, versioning, etc)

In meta-prefect, we can simplify this by using a custom "local run deployer" that is built by chaining together deployment builders.


Note that local_flow can be defined once by the experts and used by the rest of the team to deploy flows locally.

When the flow is deployed, the deployer will:
- ensure a local work pool
- ensure a local worker
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
