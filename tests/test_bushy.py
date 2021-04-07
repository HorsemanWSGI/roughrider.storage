import uuid
import io
from pathlib import Path
from reiter.upload.meta import FileInfo
from reiter.upload.bushy import BushyStorage
from unittest import mock


TEST_UUIDS = 0x12345678123456781234567812345678
FILE = io.BytesIO(b"some initial binary data: \x00\x01")

def mock_uuid():
    global TEST_UUIDS
    TEST_UUIDS += 1
    return uuid.UUID(int=TEST_UUIDS)


@mock.patch('uuid.uuid1', mock_uuid)
def test_ticketing(tmp_path):
    bushy = BushyStorage('bushy', tmp_path)
    ticket = bushy.generate_ticket()
    assert ticket == '12345678-1234-5678-1234-567812345679'

    path = bushy.ticket_to_uri(ticket)
    assert path == (
        tmp_path / '1234' / '5678' / '1234-5678-1234-567812345679')


@mock.patch('uuid.uuid1', mock_uuid)
def test_persisting(tmp_path):
    bushy = BushyStorage('bushy', tmp_path)
    storage_info = bushy.store(FILE)
    assert storage_info == FileInfo(
            storage='bushy',
            ticket='12345678-1234-5678-1234-56781234567a',
            size=28,
            checksum='53195454e1210adae36ecb34453a1f5a',
            metadata={}
        )
