"""Versioning implementations."""
from .package_based import pacakge_based_versioning
from .simple_increment import simple_increment_versioning

__all__ = ["pacakge_based_versioning", "simple_increment_versioning"]
