"""Worker implementation."""
import subprocess
import uuid
from logging import getLogger

from prefect.client.schemas.objects import Worker as ClientWorker
from prefect.utilities.asyncutils import sync_compatible
from pydantic import BaseModel, Field

from meta_prefect.implementations.utils import get_machine_id

logger = getLogger(__name__)


def gen_worker_name() -> str:
    """Generate a worker name."""
    uuid_str = str(uuid.uuid4())[:4]
    return f"ProcessWorker -- {get_machine_id()} -- {uuid_str}"


class ProcessWorker(BaseModel):
    """Process Worker."""

    name: str = Field(default_factory=gen_worker_name)
    work_pool_name: str

    @classmethod
    def from_client_worker(
        cls, worker: "ClientWorker", work_pool_name: str
    ) -> "ProcessWorker":
        """Create a process worker from a client worker."""
        return cls.parse_obj({**worker.dict(), **dict(work_pool_name=work_pool_name)})

    @sync_compatible
    async def create(self) -> None:
        subprocess.Popen(
            [
                "nohup",
                "prefect",
                "worker",
                "start",
                "--name",
                self.name,
                "--pool",
                self.work_pool_name,
            ]
        )
