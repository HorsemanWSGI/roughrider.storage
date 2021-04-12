import nanoid
from pathlib import Path
from roughrider.storage.fs import FilesystemStorage


class FlatStorage(FilesystemStorage):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id_size = kwargs.get('id_size', 16)

    def generate_ticket(self) -> str:
        return nanoid.generate(
            '_-23456789abcdefghijkmnpqrstuvwxyzABCDEFGHIJKMNPQRSTUVWXYZ',
            size=self.id_size)

    def ticket_to_uri(self, uid: str) -> Path:
        return self.root / uid
