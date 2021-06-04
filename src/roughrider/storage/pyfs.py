try:
    from typing import Iterable, BinaryIO, Type, ClassVar
    from pathlib import Path
    from fs.base import FS
    from roughrider.storage.meta import FileInfo, Storage, ChecksumAlgorithm


    class PyFSStorage(Storage):

        fs: FS
        checksum_algorithm: ChecksumAlgorithm

        def __init__(self, name: str, fs: FS, algorithm='md5'):
            self.name = name
            self.fs = fs
            try:
                self.checksum_algorithm = ChecksumAlgorithm[algorithm]
            except KeyError:
                raise LookupError(f'Unknown algorithm: `{algorithm}`.')

        def retrieve(self, ticket: str) -> Iterable[bytes]:
            path = self.ticket_to_uri(ticket)
            if not self.fs.exists(str(path)):
                raise FileNotFoundError(path)

            def file_iterator(path: Path, chunk=4096):
                with self.fs.openbin(str(path)) as reader:
                    while True:
                        data = reader.read(chunk)
                        if not data:
                            break
                        yield data

            return file_iterator(path)

        def delete(self, ticket: str) -> Iterable[bytes]:
            path = self.ticket_to_uri(ticket)
            try:
                self.fs.remove(str(path))
                return True
            except FileNotFoundError:
                raise  # we need to propagate.
            return False

        def store(self, data: BinaryIO, **metadata) -> FileInfo:
            ticket = self.generate_ticket()
            path = self.ticket_to_uri(ticket)
            self.fs.makedirs(str(path.parent), recreate=True)
            size = 0
            fhash = self.checksum_algorithm.value()
            with self.fs.openbin(str(path), mode='w+') as target:
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
except ImportError:
    pass
