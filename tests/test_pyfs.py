import uuid
import pytest
from pathlib import Path
from typing import Iterator


def pyfs_installed():
    try:
        import fs  # noqa F401
        return True
    except ImportError:
        return False


@pytest.mark.skipif(not pyfs_installed(), reason="PyFilesystem needed.")
def test_bushy_pyfs(test_file):
    from fs.memoryfs import MemoryFS
    from fs.tempfs import TempFS
    from fs.errors import ResourceNotFound
    from roughrider.storage.pyfs import PyFSStorage
    from roughrider.storage.meta import FileInfo


    class BushyStorage(PyFSStorage):

        count = None

        def generate_ticket(self) -> str:
            if self.count is None:
                self.count = 0
            self.count += 1
            return str(uuid.UUID(int=self.count))

        def ticket_to_uri(self, uid: str) -> Path:
            return Path(f'{uid[0:4]}/{uid[4:8]}/{uid[9:]}')


    storage = BushyStorage('bushy', fs=MemoryFS())
    storage_info = storage.store(test_file)
    assert storage_info == FileInfo(
        namespace='bushy',
        ticket='00000000-0000-0000-0000-000000000001',
        size=28,
        checksum=('md5', '53195454e1210adae36ecb34453a1f5a'),
        metadata={}
    )
    iterator = storage.retrieve(storage_info['ticket'])
    assert isinstance(iterator, Iterator)
    test_file.seek(0)
    assert b''.join(iterator) == test_file.read()
    test_file.seek(0)

    storage.delete(storage_info['ticket'])

    with pytest.raises(ResourceNotFound):
        storage.delete(storage_info['ticket'])


    storage = BushyStorage('bushy', fs=TempFS())
    storage_info = storage.store(test_file)
    assert storage_info == FileInfo(
        namespace='bushy',
        ticket='00000000-0000-0000-0000-000000000001',
        size=28,
        checksum=('md5', '53195454e1210adae36ecb34453a1f5a'),
        metadata={}
    )
    iterator = storage.retrieve(storage_info['ticket'])
    assert isinstance(iterator, Iterator)
    test_file.seek(0)
    assert b''.join(iterator) == test_file.read()
    test_file.seek(0)

    storage.delete(storage_info['ticket'])

    with pytest.raises(ResourceNotFound):
        storage.delete(storage_info['ticket'])
