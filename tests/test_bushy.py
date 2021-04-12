import pytest
import uuid
from unittest import mock
from typing import Iterator
from roughrider.storage.meta import FileInfo
from roughrider.storage.bushy import BushyStorage


def mock_uuid():
    return uuid.UUID(int=0x12345678123456781234567812345678)


@mock.patch('uuid.uuid1', mock_uuid)
def test_ticket(tmp_path):
    storage = BushyStorage('bushy', tmp_path)
    ticket = storage.generate_ticket()
    assert ticket == '12345678-1234-5678-1234-567812345678'

    path = storage.ticket_to_uri(ticket)
    assert path == (
        tmp_path / '1234' / '5678' / '1234-5678-1234-567812345678')

    with pytest.raises(ValueError) as exc:
        storage.ticket_to_uri('random ticket')
    assert str(exc.value) == 'Invalid ticket format.'


@mock.patch('uuid.uuid1', mock_uuid)
def test_store(test_file, tmp_path):
    storage = BushyStorage('bushy', tmp_path)
    storage_info = storage.store(test_file)
    assert storage_info == FileInfo(
        namespace='bushy',
        ticket='12345678-1234-5678-1234-567812345678',
        size=28,
        checksum=('md5', '53195454e1210adae36ecb34453a1f5a'),
        metadata={}
    )


@mock.patch('uuid.uuid1', mock_uuid)
def test_store_metadata(test_file, tmp_path):
    storage = BushyStorage('bushy', tmp_path)
    storage_info = storage.store(
        test_file, filename="test.jpg", owner="admin")
    assert storage_info == FileInfo(
        namespace='bushy',
        ticket='12345678-1234-5678-1234-567812345678',
        size=28,
        checksum=('md5', '53195454e1210adae36ecb34453a1f5a'),
        metadata={'filename': 'test.jpg', 'owner': 'admin'}
    )


def test_retrieve(test_file, tmp_path):
    storage = BushyStorage('bushy', tmp_path)
    storage_info = storage.store(test_file)
    iterator = storage.retrieve(storage_info['ticket'])
    assert isinstance(iterator, Iterator)
    test_file.seek(0)
    assert b''.join(iterator) == test_file.read()


def test_delete(test_file, tmp_path):
    storage = BushyStorage('bushy', tmp_path)
    storage_info = storage.store(test_file)
    storage.delete(storage_info['ticket'])

    with pytest.raises(FileNotFoundError):
        storage.delete(storage_info['ticket'])


def test_checksum(test_file, tmp_path):
    storage = BushyStorage('bushy', tmp_path, algorithm="sha256")
    storage_info = storage.store(test_file)
    assert storage_info['checksum'] == (
        'sha256',
        '18e9b7c9c1be46b1c62938b11b02f513a4d507630c4aee744799df83e0a94ba6'
    )
    with pytest.raises(LookupError) as exc:
        BushyStorage('bushy', tmp_path, algorithm="pouet")
    assert str(exc.value) == "Unknown algorithm: `pouet`."
