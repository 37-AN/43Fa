from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ConnectorSchemaField:
    name: str
    data_type: str
    nullable: bool = True


@dataclass(frozen=True)
class ConnectorMetadata:
    connector_type: str
    display_name: str
    read_only: bool = True
    supports_incremental: bool = True


class BaseConnector(ABC):
    """Common contract for all source connectors."""

    @property
    @abstractmethod
    def max_batch_size(self) -> int:
        """Maximum records to fetch per incremental call."""

    @property
    @abstractmethod
    def connector_metadata(self) -> ConnectorMetadata:
        """Static metadata describing connector capabilities."""

    @abstractmethod
    def test_connection(self) -> bool:
        """Returns True when connector can reach the source safely."""

    @abstractmethod
    def discover_schema(self) -> list[ConnectorSchemaField]:
        """Returns source schema fields available for mapping."""

    @abstractmethod
    def fetch_incremental(
        self,
        cursor_state: dict[str, Any] | None,
    ) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
        """
        Fetch incremental rows and return updated cursor state.
        Implementations must be side-effect free on the source system.
        """
