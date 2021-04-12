import re
import uuid
from pathlib import Path
from roughrider.storage.fs import FilesystemStorage


UUID = re.compile(
    "^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$")


class BushyStorage(FilesystemStorage):

    def generate_ticket(self) -> str:
        return str(uuid.uuid1())

    def ticket_to_uri(self, uid: str) -> Path:
        if not UUID.match(uid):
            raise ValueError('Invalid ticket format.')
        return self.root / uid[0:4] / uid[4:8] / uid[9:]
