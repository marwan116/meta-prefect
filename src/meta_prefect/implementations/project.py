"""Project specification."""
from typing import Any, Dict, List

from pydantic import BaseModel

FlowNameStr = str


class DeploymentSpec(BaseModel):
    """Deployment specification"""

    recipe: str
    variables: Dict[str, Any]


class ProjectSpec(BaseModel):
    """Project specification."""

    deployments: Dict[FlowNameStr, List[DeploymentSpec]]
