import nanoid
from pathlib import Path
from reiter.upload.fs import FilesystemStorage


class FlatStorage(FilesystemStorage):

    def __init__(self, name: str, root: Path, id_size: int=16):
        self.name = name
        self.root = root
        self.id_size = 16

    def generate_ticket(self) -> str:
        return nanoid.generate(
            '_-23456789abcdefghijkmnpqrstuvwxyzABCDEFGHIJKMNPQRSTUVWXYZ',
            size=self.id_size)

    def ticket_to_uri(self, uid: str) -> Path:
        return self.root / uid
