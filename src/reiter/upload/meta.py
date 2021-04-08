from abc import ABC, abstractmethod
from typing_extensions import TypedDict
from typing import Optional, BinaryIO, Mapping, Iterable
from pathlib import Path


class FileInfo(TypedDict):
    ticket: str
    size: int
    checksum: str
    storage: str
    metadata: Optional[dict] = None


class Storage(ABC):
    name: str
    root: Path

    @abstractmethod
    def generate_ticket(self) -> str:
        pass

    @abstractmethod
    def retrieve(self, ticket: str) -> Iterable[bytes]:
        pass

    @abstractmethod
    def store(self, data: BinaryIO, **metadata) -> FileInfo:
        pass


class Uploader:
    namespaces: Mapping[str, Storage]

    def get(self, info: FileInfo):
        namespace = namespace.get(info.namespace)
        if namespace is None:
            raise LookupError(
                f'Namespace `{info.namespace}` does not exist.')
        return namespace.retrieve(info.ticket)
