import pytest
from roughrider.storage.meta import StorageCenter, FileInfo
from roughrider.storage.flat import FlatStorage


def test_empty_store(test_file):
    center = StorageCenter()
    with pytest.raises(LookupError) as exc:
        center.store('somewhere', test_file)
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
        checksum=('md5', '53195454e1210adae36ecb34453a1f5a'),
        metadata={}
    )
    with pytest.raises(LookupError) as exc:
        center[info]
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


def test_store_get_retrieve_delete(test_file, tmp_path):
    center = StorageCenter()
    flat = FlatStorage('somewhere', tmp_path)
    center.register(flat)

    info = center.store('somewhere', test_file)
    assert isinstance(info, dict)

    test_file.seek(0)
    fiter = center[info]
    assert b''.join(fiter) == test_file.read()

    test_file.seek(0)
    fiter = center.retrieve('somewhere', info['ticket'])
    assert b''.join(fiter) == test_file.read()

    del center[info]
    with pytest.raises(FileNotFoundError):
        center.retrieve('somewhere', info['ticket'])
