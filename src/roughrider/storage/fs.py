from typing import Iterable, BinaryIO
from pathlib import Path
from roughrider.storage.meta import FileInfo, Storage, ChecksumAlgorithm


class FilesystemStorage(Storage):

    checksum_algorithm: ChecksumAlgorithm

    def __init__(self, name: str, root: Path, algorithm='md5'):
        self.name = name
        self.root = root
        try:
            self.checksum_algorithm = ChecksumAlgorithm[algorithm]
        except KeyError:
            raise LookupError(f'Unknown algorithm: `{algorithm}`.')

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
        if not path.exists():
            raise FileNotFoundError(path)
        return self.file_iterator(path)

    def delete(self, ticket: str) -> Iterable[bytes]:
        path = self.ticket_to_uri(ticket)
        try:
            path.unlink()
            return True
        except FileNotFoundError:
            raise  # we need to propagate.
        return False

    def store(self, data: BinaryIO, **metadata) -> FileInfo:
        ticket = self.generate_ticket()
        path = self.ticket_to_uri(ticket)
        assert not path.exists()  # this happens on ticket conflicts.
        depth = len(path.relative_to(self.root).parents)
        if depth > 1:
            path.parent.mkdir(mode=0o755, parents=True, exist_ok=False)
        size = 0
        fhash = self.checksum_algorithm.value()
        with path.open('wb+') as target:
            for block in iter(lambda: data.read(4096), b""):
                size += target.write(block)
                fhash.update(block)

        return FileInfo(
            namespace=self.name,
            ticket=ticket,
            size=size,
            checksum=(fhash.name, fhash.hexdigest()),
            metadata=metadata
        )
