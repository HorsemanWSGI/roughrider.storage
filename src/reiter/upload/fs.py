import hashlib
from typing import Iterable, BinaryIO
from pathlib import Path
from reiter.upload.meta import FileInfo, Storage


class FilesystemStorage(Storage):

    def __init__(self, name: str, root: Path):
        self.name = name
        self.root = root

    @staticmethod
    def file_iterator(path: Path, chunk=4096):
        with path.open('rb') as reader:
            while True:
                data = reader.read(chunk)
                if not data:
                    break
                yield data

    def retrieve(self, ticket: str) -> Iterable[bytes]:
        path = self.ticket_to_uri(ticket)
        assert path.exists()
        return self.file_iterator(path)

    def store(self, data: BinaryIO, **metadata) -> FileInfo:
        ticket = self.generate_ticket()
        path = self.ticket_to_uri(ticket)
        depth = len(path.relative_to(self.root).parents)
        if depth > 1:
            path.parent.mkdir(mode=0o755, parents=True, exist_ok=False)
        size = 0
        hash_md5 = hashlib.md5()
        with path.open('wb+') as target:
            for block in iter(lambda: data.read(4096), b""):
                size += target.write(block)
                hash_md5.update(block)

        return FileInfo(
            storage=self.name,
            ticket=ticket,
            size=size,
            checksum=hash_md5.hexdigest(),
            metadata=metadata
        )
