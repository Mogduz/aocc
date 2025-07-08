import os
import pickle
import pytest

from aocc.src.fileobject import FileObject

def test_exists_and_is_file(tmp_path):
    # Non-existent path
    path = tmp_path / "nonexistent"
    fo = FileObject(str(path))
    assert not fo.exists()
    assert not fo.is_file()

    # Create a file by writing bytes
    data = b"hello"
    path.write_bytes(data)
    assert fo.exists()
    assert fo.is_file()


def test_is_file_for_directory(tmp_path):
    # Directory should exist but not be a file
    path = tmp_path / "dir"
    path.mkdir()
    fo = FileObject(str(path))
    assert fo.exists()
    assert not fo.is_file()


def test_write_and_read_bytes(tmp_path):
    path = tmp_path / "file.bin"
    fo = FileObject(str(path))
    data = b"test data"

    # Write bytes and verify length
    written = fo.write_bytes(data)
    assert written == len(data)

    # Read back and compare
    read = fo.read_bytes()
    assert read == data


def test_read_bytes_file_not_found(tmp_path):
    path = tmp_path / "nofile.bin"
    fo = FileObject(str(path))
    # Reading non-existent file should raise FileNotFoundError
    with pytest.raises(FileNotFoundError):
        fo.read_bytes()


def test_write_and_read_empty_bytes(tmp_path):
    path = tmp_path / "empty.bin"
    fo = FileObject(str(path))
    data = b""

    # Writing empty bytes returns 0
    written = fo.write_bytes(data)
    assert written == 0

    # Reading yields empty bytes
    assert fo.read_bytes() == data


def test_read_object_and_write_object(tmp_path):
    path = tmp_path / "obj.pkl"
    fo = FileObject(str(path))
    obj = {"key": ["list", 123], "nested": {"a": 1.23}}

    # Write object and verify success
    assert fo.write_object(obj)

    # File should exist
    assert path.exists()

    # Read object and compare
    assert fo.read_object() == obj


def test_write_and_read_empty_object(tmp_path):
    path = tmp_path / "none.pkl"
    fo = FileObject(str(path))

    # Writing and reading None
    assert fo.write_object(None)
    assert fo.read_object() is None


def test_write_object_failure(monkeypatch, tmp_path):
    path = tmp_path / "fail.pkl"
    fo = FileObject(str(path))

    # Monkeypatch write_bytes to simulate incomplete write
    def fake_write_bytes(data):
        # Actually write full data to file
        with open(path, "wb") as f:
            f.write(data)
        # Return one byte less to simulate failure
        return len(data) - 1

    monkeypatch.setattr(fo, "write_bytes", fake_write_bytes)

    # write_object should detect mismatch and return False
    assert not fo.write_object({"a": 1})
