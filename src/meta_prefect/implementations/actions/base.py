"""Base action implementation."""
from abc import ABC, abstractmethod
from typing import Any, Dict, FrozenSet

from pydantic import BaseModel, Field, PrivateAttr

# TODO - use weakref.WeakKeyDictionary() instead but it doesn't work with
# frozen pydantic models
cache: Dict["Action", Any] = {}  # weakref.WeakKeyDictionary()


class Action(BaseModel, ABC):
    """An action."""

    requires: FrozenSet["Action"] = Field(
        default_factory=frozenset,
        description="The actions that must be run before this action.",
    )

    _outputs: Any = PrivateAttr(default=None)

    @property
    def result(self) -> Any:
        """Get the result of the action."""
        try:
            return cache[self]
        except KeyError:
            raise RuntimeError("Action has not been run yet.")

    async def run(self) -> Any:
        """Run the action."""
        if self not in cache:
            cache[self] = await self._run()
        return cache[self]

    @abstractmethod
    async def _run(self) -> Any:
        ...

    class Config:
        frozen = True

    def __eq__(self, other):
        return isinstance(other, Action) and hash(self) == hash(other)
