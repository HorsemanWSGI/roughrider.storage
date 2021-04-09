import enum
import hashlib
from abc import ABC, abstractmethod
from functools import partial
from pathlib import Path
from typing import Optional, BinaryIO, Mapping, Iterable, Tuple
from typing_extensions import TypedDict


ChecksumAlgorithm = enum.Enum(
    'Algorithm', {
        name: partial(hashlib.new, name)
        for name in hashlib.algorithms_available
    }
)


class FileInfo(TypedDict):
    ticket: str
    size: int
    checksum: Tuple[str, str]  # (algorithm, value)
    namespace: str
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


class StorageCenter:
    namespaces: Mapping[str, Storage]

    def __init__(self):
        self.namespaces = {}

    def get(self, info: FileInfo) -> Iterable[bytes]:
        return self.retrieve(info['namespace'], info['ticket'])

    def register(self, storage: Storage):
        if storage.name in self.namespaces:
            raise NameError(f'Namespace `{storage.name}` already exists.')
        self.namespaces[storage.name] = storage

    def store(self, namespace: str, data: BinaryIO, **metadata) -> FileInfo:
        storage = self.namespaces.get(namespace)
        if storage is None:
            raise LookupError(f'Namespace `{namespace}` is unknown.')
        return storage.store(data, **metadata)

    def retrieve(self, namespace: str, ticket: str) -> Iterable[bytes]:
        storage = self.namespaces.get(namespace)
        if storage is None:
            raise LookupError(f'Namespace `{namespace}` is unknown.')
        return storage.retrieve(ticket)
