"""Class registry implementation."""
from typing import Iterator, MutableMapping, TypeVar

KeyT = TypeVar("KeyT")
ValueT = TypeVar("ValueT")


class ClassRegistry(MutableMapping[KeyT, ValueT]):
    """A class registry."""

    def __init__(self) -> None:
        self._data = {}

    def register(self, cls: ValueT) -> None:
        self._data[cls.__name__] = cls

    def get(self, name: KeyT) -> ValueT:
        return self._data.get(name)

    def __getitem__(self, key: KeyT) -> ValueT:
        return self._data[key]

    def __setitem__(self, key: KeyT, value: ValueT) -> None:
        self._data[key] = value

    def __delitem__(self, key: KeyT) -> None:
        del self._data[key]

    def __iter__(self) -> Iterator[KeyT]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)
