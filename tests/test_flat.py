import pytest
import re
from typing import Iterator
from reiter.upload.meta import FileInfo
from reiter.upload.flat import FlatStorage
from unittest import mock


def nanoid_generator():
    yield 'my_tiny_id'
    yield 'my_other_id'
    yield 'yet-another-id'


def mock_nanoid():
    generator = nanoid_generator()

    def mock_generator(vocabulary, size=16):
        return next(generator)

    return mock_generator


@mock.patch('nanoid.generate', mock_nanoid())
def test_ticketing(tmp_path):
    flat = FlatStorage('flat', tmp_path)
    ticket = flat.generate_ticket()
    assert ticket == 'my_tiny_id'
    path = flat.ticket_to_uri(ticket)
    assert path == tmp_path / ticket


@mock.patch('nanoid.generate', mock_nanoid())
def test_persisting(test_file, tmp_path):
    flat = FlatStorage('flat', tmp_path)
    storage_info = flat.store(test_file)
    assert storage_info == FileInfo(
            namespace='flat',
            ticket='my_tiny_id',
            size=28,
            checksum=('md5', '53195454e1210adae36ecb34453a1f5a'),
            metadata={}
        )


def test_retrieving(test_file, tmp_path):
    flat = FlatStorage('flat', tmp_path)
    storage_info = flat.store(test_file)
    iterator = flat.retrieve(storage_info['ticket'])
    assert isinstance(iterator, Iterator)
    test_file.seek(0)
    assert b''.join(iterator) == test_file.read()


def test_id_format(tmp_path):
    flat = FlatStorage('flat', tmp_path)
    ticket = flat.generate_ticket()
    assert len(ticket) == 16
    assert re.match(r'[^\w\-]', ticket) is None

    flat.id_size = 10
    ticket = flat.generate_ticket()
    assert len(ticket) == 10
    assert re.match(r'[^\w\-]', ticket) is None


def test_checksum(test_file, tmp_path):
    flat = FlatStorage('flat', tmp_path, algorithm="sha256")
    storage_info = flat.store(test_file)
    assert storage_info['checksum'] == (
        'sha256',
        '18e9b7c9c1be46b1c62938b11b02f513a4d507630c4aee744799df83e0a94ba6'
    )

    with pytest.raises(LookupError) as exc:
        FlatStorage('flat', tmp_path, algorithm="pouet")
    assert str(exc.value) == "Unknown algorithm: `pouet`."
