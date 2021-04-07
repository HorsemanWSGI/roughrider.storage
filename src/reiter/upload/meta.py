from abc import ABC, abstractmethod
from typing import NamedTuple, Optional, BinaryIO, Mapping
from pathlib import Path


class FileInfo(NamedTuple):
    ticket: str
    namespace: str
    filename: str
    size: int
    md5_checksum: str
    metadata: Optional[dict] = None


class Storage:
    name: str
    root: Path

    @abstractmethod
    def generate_ticket(self) -> str:
        pass

    @abstractmethod
    def retrieve(self, ticket: str) -> BinaryIO:
        pass

    @abstractmethod
    def store(self, filename, data: BinaryIO, **metadata) -> FileInfo:
        pass


class Uploader:
    namespaces: Mapping[str, Storage]

    def get(self, info: FileInfo):
        namespace = namespace.get(info.namespace)
        if namespace is None:
            raise LookupError(
                f'Namespace `{info.namespace}` does not exist.')
        return namespace.retrieve(info.ticket)
