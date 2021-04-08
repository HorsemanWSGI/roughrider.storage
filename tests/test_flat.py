import nanoid
import uuid
import io
import re
from typing import BinaryIO, Iterator
from pathlib import Path
from reiter.upload.meta import FileInfo
from reiter.upload.flat import FlatStorage
from unittest import mock


FILE = io.BytesIO(b"some initial binary data: \x00\x01")


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
def test_persisting(tmp_path):
    flat = FlatStorage('flat', tmp_path)
    storage_info = flat.store(FILE)
    assert storage_info == FileInfo(
            namespace='flat',
            ticket='my_tiny_id',
            size=28,
            checksum='53195454e1210adae36ecb34453a1f5a',
            metadata={}
        )


def test_retrieving(tmp_path):
    flat = FlatStorage('flat', tmp_path)
    storage_info = flat.store(FILE)
    iterator = flat.retrieve(storage_info['ticket'])
    assert isinstance(iterator, Iterator)
    assert b''.join(iterator) == FILE.read()


def test_id_format(tmp_path):
    flat = FlatStorage('flat', tmp_path)
    ticket = flat.generate_ticket()
    assert len(ticket) == 16
    assert re.match(r'[^\w\-]', ticket) == None

    flat.id_size = 10
    ticket = flat.generate_ticket()
    assert len(ticket) == 10
    assert re.match(r'[^\w\-]', ticket) == None
