import enum
import hashlib
from abc import ABC, abstractmethod
from functools import partial
from pathlib import Path
from typing import TypedDict, BinaryIO, MutableMapping, Iterable, Tuple


ChecksumAlgorithm = enum.Enum(
    'Algorithm', {
        name: getattr(hashlib, name)
        for name in hashlib.algorithms_guaranteed
    }
)


class FileInfo(TypedDict):
    ticket: str
    size: int
    checksum: tuple[str, str]  # (algorithm, value)
    namespace: str
    metadata: dict | None = None


class Storage(ABC):
    name: str
    root: Path

    @abstractmethod
    def generate_ticket(self) -> str:
        pass

    @abstractmethod
    def ticket_to_uri(self, uid: str) -> Path:
        pass

    @abstractmethod
    def retrieve(self, ticket: str) -> Iterable[bytes]:
        pass

    @abstractmethod
    def store(self, data: BinaryIO, **metadata) -> FileInfo:
        pass

    @abstractmethod
    def delete(self, ticket: str) -> bool:
        pass


class StorageCenter:

    __slots__ = ('namespaces',)

    namespaces: MutableMapping[str, Storage]

    def __init__(self, namespaces=None):
        if namespaces is None:
            namespaces = {}
        self.namespaces = namespaces

    def __getitem__(self, info: FileInfo) -> Iterable[bytes]:
        return self.retrieve(info['namespace'], info['ticket'])

    def __delitem__(self, info: FileInfo):
        return self.delete(info['namespace'], info['ticket'])

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

    def delete(self, namespace: str, ticket: str) -> bool:
        storage = self.namespaces.get(namespace)
        if storage is None:
            raise LookupError(f'Namespace `{namespace}` is unknown.')
        return storage.delete(ticket)
