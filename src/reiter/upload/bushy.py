import re
import uuid
import shutil
import hashlib
from pathlib import Path
from reiter.upload.meta import Storage, FileInfo
from typing import BinaryIO


UUID = re.compile(
    "^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$")


class BushyStorage(Storage):

    def __init__(self, name: str, root: Path):
        self.name = name
        self.root = root

    def generate_ticket(self) -> str:
        return str(uuid.uuid1())

    def ticket_to_uri(self, uid: str) -> Path:
        if not UUID.match(uid):
            raise KeyError('Invalid ticket format.')
        return self.root / uid[0:4] / uid[4:8] / uid[9:]

    def retrieve(self, ticket: str) -> BinaryIO:
        pass

    def store(self, data: BinaryIO, **metadata) -> FileInfo:
        ticket = self.generate_ticket()
        path = self.ticket_to_uri(ticket)
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
