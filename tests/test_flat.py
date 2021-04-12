import pytest
import re
from typing import Iterator
from roughrider.storage.meta import FileInfo
from roughrider.storage.flat import FlatStorage
from unittest import mock


def mock_nanoid(*args, **kwargs):
    return 'my_tiny_id'


@mock.patch('nanoid.generate', mock_nanoid)
def test_ticket(tmp_path):
    storage = FlatStorage('flat', tmp_path)
    ticket = storage.generate_ticket()
    assert ticket == 'my_tiny_id'
    path = storage.ticket_to_uri(ticket)
    assert path == tmp_path / ticket


def test_ticket_format(tmp_path):
    storage = FlatStorage('flat', tmp_path)
    ticket = storage.generate_ticket()
    assert len(ticket) == 16
    assert re.match(r'[^\w\-]', ticket) is None

    storage.id_size = 10
    ticket = storage.generate_ticket()
    assert len(ticket) == 10
    assert re.match(r'[^\w\-]', ticket) is None


@mock.patch('nanoid.generate', mock_nanoid)
def test_store(test_file, tmp_path):
    storage = FlatStorage('flat', tmp_path)
    storage_info = storage.store(test_file)
    assert storage_info == FileInfo(
        namespace='flat',
        ticket='my_tiny_id',
        size=28,
        checksum=('md5', '53195454e1210adae36ecb34453a1f5a'),
        metadata={}
    )


def test_retrieve(test_file, tmp_path):
    storage = FlatStorage('flat', tmp_path)
    storage_info = storage.store(test_file)
    iterator = storage.retrieve(storage_info['ticket'])
    assert isinstance(iterator, Iterator)
    test_file.seek(0)
    assert b''.join(iterator) == test_file.read()


def test_delete(test_file, tmp_path):
    storage = FlatStorage('flat', tmp_path)
    storage_info = storage.store(test_file)
    storage.delete(storage_info['ticket'])

    with pytest.raises(FileNotFoundError):
        storage.delete(storage_info['ticket'])


def test_checksum(test_file, tmp_path):
    storage = FlatStorage('flat', tmp_path, algorithm="sha256")
    storage_info = storage.store(test_file)
    assert storage_info['checksum'] == (
        'sha256',
        '18e9b7c9c1be46b1c62938b11b02f513a4d507630c4aee744799df83e0a94ba6'
    )

    with pytest.raises(LookupError) as exc:
        FlatStorage('flat', tmp_path, algorithm="pouet")
    assert str(exc.value) == "Unknown algorithm: `pouet`."
