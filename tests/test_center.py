import io
import pytest
from reiter.upload.meta import StorageCenter
from reiter.upload.flat import FlatStorage
from typing import BinaryIO
from reiter.upload.meta import FileInfo
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


def test_empty_store():
    center = StorageCenter()
    with pytest.raises(LookupError) as exc:
        center.store('somewhere', FILE)
    assert str(exc.value) == 'Namespace `somewhere` is unknown.'


def test_empty_retrieve():
    center = StorageCenter()
    with pytest.raises(LookupError) as exc:
        center.retrieve('somewhere', 'bogus_id')
    assert str(exc.value) == 'Namespace `somewhere` is unknown.'


def test_empty_get():
    center = StorageCenter()
    info = FileInfo(
        namespace='somewhere',
        ticket='12345678-1234-5678-1234-56781234567a',
        size=28,
        checksum='53195454e1210adae36ecb34453a1f5a',
        metadata={}
    )
    with pytest.raises(LookupError) as exc:
        center.get(info)
    assert str(exc.value) == 'Namespace `somewhere` is unknown.'


def test_register(tmp_path):
    center = StorageCenter()
    flat = FlatStorage('somewhere', tmp_path)
    center.register(flat)
    assert 'somewhere' in center.namespaces

    someother = FlatStorage('somewhere', tmp_path)
    with pytest.raises(NameError) as exc:
        center.register(someother)
    assert str(exc.value) == 'Namespace `somewhere` already exists.'


@mock.patch('nanoid.generate', mock_nanoid())
def test_store_get_retrieve(tmp_path):
    center = StorageCenter()
    flat = FlatStorage('somewhere', tmp_path)
    center.register(flat)
    info = center.store('somewhere', FILE)
    assert info == FileInfo(
        namespace='somewhere',
        ticket='my_tiny_id',
        size=28,
        checksum='53195454e1210adae36ecb34453a1f5a',
        metadata={}
    )
