from abc import ABC, abstract_method
from typing import NamedTuple, Optional, BinaryIO


class FileInfo(typing.NamedTuple):
    ticket: str
    namespace: str
    filename: str
    size: int
    md5_checksum: str
    metadata: Optional[dict] = None


class Storage:
    name: str

    @abstract_method
    def generate_ticket(self) -> str:
        pass

    @abstract_method
    def retrieve(self, ticket: str) -> BinaryIO:
        pass

    @abstract_method
    def store(self, filename, data: BinaryIO, **metadata) -> FileInfo:
        pass


class Uploader:
    namespaces: Mapping[str, Storage]

    def get(self, metadata: FileMetadata):
        namespace = namespace.get(metadata.namespace)
        if namespace is None:
            raise LookupError(
                f'Namespace `{metadata.namespace}` does not exist.')
        return namespace.retrieve(metadata.ticket)
