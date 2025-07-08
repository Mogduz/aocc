import os
import pickle
import pytest

from aocc.src.fileobject import FileObject


def test_exists_and_is_file(tmp_path):
    # Path does not exist
    path = tmp_path / "nonexistent"
    fo = FileObject(str(path))
    assert not fo.exists()
    assert not fo.is_file()

    # Create a file and test
    data = b"hello"
    path.write_bytes(data)
    assert fo.exists()
    assert fo.is_file()


def test_is_file_for_directory(tmp_path):
    # Directory should exist but not be a file
    dir_path = tmp_path / "dir"
    dir_path.mkdir()
    fo = FileObject(str(dir_path))
    assert fo.exists()
    assert not fo.is_file()


def test_read_bytes_nonexistent_and_directory(tmp_path):
    # Non-existent file should return empty bytes
    path = tmp_path / "nofile"
    fo = FileObject(str(path))
    assert fo.read_bytes() == b""

    # Directory should return empty bytes
    dir_path = tmp_path / "dir"
    dir_path.mkdir()
    fo_dir = FileObject(str(dir_path))
    assert fo_dir.read_bytes() == b""


def test_write_and_read_bytes(tmp_path):
    path = tmp_path / "file.bin"
    fo = FileObject(str(path))
    data = b"test data"

    # Write and verify length
    written = fo.write_bytes(data)
    assert written == len(data)

    # Read via pathlib and via FileObject
    assert path.read_bytes() == data
    assert fo.read_bytes() == data

    # Overwrite with new data
    new_data = b"new"
    written2 = fo.write_bytes(new_data)
    assert written2 == len(new_data)
    assert fo.read_bytes() == new_data


def test_write_bytes_empty(tmp_path):
    path = tmp_path / "empty.bin"
    fo = FileObject(str(path))
    # Writing empty bytes returns 0
    assert fo.write_bytes(b"") == 0
    # Reading yields empty bytes
    assert fo.read_bytes() == b""


def test_write_bytes_to_directory_raises(tmp_path):
    # Attempting to write bytes to a directory should raise OSError
    dir_path = tmp_path / "dir"
    dir_path.mkdir()
    fo = FileObject(str(dir_path))
    with pytest.raises(OSError):
        fo.write_bytes(b"data")


def test_read_object_empty_invalid_and_directory(tmp_path):
    # Non-existent path
    path = tmp_path / "data.obj"
    fo = FileObject(str(path))
    assert fo.read_object() is None

    # Empty file
    path.write_bytes(b"")
    assert fo.read_object() is None

    # Invalid pickle data
    path.write_bytes(b"not a pickle")
    assert fo.read_object() is None

    # Directory path should also yield None
    dir_path = tmp_path / "dir"
    dir_path.mkdir()
    fo_dir = FileObject(str(dir_path))
    assert fo_dir.read_object() is None


def test_write_and_read_object(tmp_path):
    path = tmp_path / "obj.pkl"
    fo = FileObject(str(path))
    obj = {"key": [1, 2, 3], "nested": {"a": 1.23}}

    # Write object and validate
    assert fo.write_object(obj) is True
    assert path.exists() and path.is_file()

    # Read back and compare
    assert fo.read_object() == obj


def test_write_object_empty(tmp_path):
    path = tmp_path / "none.pkl"
    fo = FileObject(str(path))

    # Writing and reading None
    assert fo.write_object(None) is True
    assert fo.read_object() is None


def test_write_object_to_directory_raises(tmp_path):
    # Attempting to write an object to a directory should raise OSError
    dir_path = tmp_path / "dir"
    dir_path.mkdir()
    fo = FileObject(str(dir_path))
    with pytest.raises(OSError):
        fo.write_object({"a": 1})


def test_write_object_failure(monkeypatch, tmp_path):
    # Simulate partial write to trigger False return
    path = tmp_path / "fail.pkl"
    fo = FileObject(str(path))

    def fake_write_bytes(data):
        # Write full data but report fewer bytes
        with open(path, "wb") as f:
            f.write(data)
        return len(data) - 1

    monkeypatch.setattr(fo, "write_bytes", fake_write_bytes)
    assert fo.write_object({"a": 1}) is False
