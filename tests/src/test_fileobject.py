import os
import pickle
import time
import sys
import pytest
import pathlib
from typing import Any, Dict, List, Optional, Tuple
from aocc.src.fileobject import FileObject


def test_exists_and_is_file(tmp_path: pathlib.Path) -> None:
    path: pathlib.Path = tmp_path / "file.txt"
    fo: FileObject = FileObject(str(path))
    assert fo.exists() is False
    assert fo.is_file() is False

    # Create file
    path.write_text("hello")
    assert fo.exists() is True
    assert fo.is_file() is True


@pytest.mark.parametrize(
    "path_name, is_dir, expected_exists, expected_is_file",
    [
        ("new.txt", False, False, False),
        ("existing.txt", False, True, True),
        ("subdir", True, True, False),
    ]
)
def test_exists_and_is_file_param(
    tmp_path: pathlib.Path,
    path_name: str,
    is_dir: bool,
    expected_exists: bool,
    expected_is_file: bool
) -> None:
    path: pathlib.Path = tmp_path / path_name
    if expected_exists and not is_dir:
        path.write_text("data")
    if is_dir:
        path.mkdir()

    fo: FileObject = FileObject(str(path))
    assert fo.exists() is expected_exists
    assert fo.is_file() is expected_is_file


def test_touch_creates_and_updates(tmp_path: pathlib.Path) -> None:
    path: pathlib.Path = tmp_path / "newfile"
    fo: FileObject = FileObject(str(path))
    assert not path.exists()
    fo.touch()
    assert path.exists() and path.is_file()

    ts_before: float = path.stat().st_mtime
    time.sleep(0.01)
    fo.touch()
    ts_after: float = path.stat().st_mtime
    assert ts_after > ts_before


def test_remove_file(tmp_path: pathlib.Path) -> None:
    path: pathlib.Path = tmp_path / "to_remove"
    path.write_text("data")
    fo: FileObject = FileObject(str(path))
    assert path.exists()
    fo.remove()
    assert not path.exists()


def test_remove_nonexistent_returns_none(tmp_path: pathlib.Path) -> None:
    path: pathlib.Path = tmp_path / "doesnotexist"
    fo: FileObject = FileObject(str(path))
    # Should return None when file doesn't exist
    result: Optional[bool] = fo.remove()
    assert result is None

def test_read_bytes_nonexistent_and_directory(tmp_path: pathlib.Path) -> None:
    path: pathlib.Path = tmp_path / "nofile.bin"
    fo: FileObject = FileObject(str(path))
    assert fo.read_bytes() == b""

    dir_path: pathlib.Path = tmp_path / "dir"
    dir_path.mkdir()
    fo_dir: FileObject = FileObject(str(dir_path))
    assert fo_dir.read_bytes() == b""


def test_write_and_read_bytes(tmp_path: pathlib.Path) -> None:
    path: pathlib.Path = tmp_path / "data.bin"
    fo: FileObject = FileObject(str(path))
    payloads: List[bytes] = [b"0123456789", b"", os.urandom(1024)]
    for data in payloads:
        length: int = fo.write_bytes(data)
        assert length == len(data)
        assert fo.read_bytes() == data


def test_write_bytes_errors(tmp_path: pathlib.Path) -> None:
    fo: FileObject = FileObject(str(tmp_path / "bad.bin"))
    with pytest.raises(TypeError):
        fo.write_bytes("notbytes")  # type: ignore

    dir_path: pathlib.Path = tmp_path / "dir"
    dir_path.mkdir()
    fo_dir: FileObject = FileObject(str(dir_path))
    with pytest.raises(OSError):
        fo_dir.write_bytes(b"data")


@pytest.mark.parametrize(
    "initial, describe",
    [
        (None, "None when no file"),
        (b"", "None on empty bytes"),
        (b"notpickle", "None on invalid pickle"),
    ]
)
def test_read_object_invalid(
    tmp_path: pathlib.Path,
    initial: Optional[bytes],
    describe: str
) -> None:
    path: pathlib.Path = tmp_path / "obj.pkl"
    if isinstance(initial, bytes):
        path.write_bytes(initial)
    fo: FileObject = FileObject(str(path))
    assert fo.read_object() is None, describe


def test_write_and_read_object_param(tmp_path: pathlib.Path) -> None:
    path: pathlib.Path = tmp_path / "test.pkl"
    fo: FileObject = FileObject(str(path))
    cases: List[Tuple[Any, Any]] = [
        (0, 0),
        ({"x": [1, 2], "y": (3, 4)}, {"x": [1, 2], "y": (3, 4)}),
        ([], []),
    ]
    for obj, expected in cases:
        assert fo.write_object(obj) is True
        assert fo.read_object() == expected


def test_write_object_unpicklable_handles_attribute_error(tmp_path: pathlib.Path) -> None:
    fo: FileObject = FileObject(str(tmp_path / "bad.pkl"))
    # AttributeError from pickle.dumps on local functions
    with pytest.raises((pickle.PicklingError, AttributeError)):
        fo.write_object(lambda z: z)


def test_write_object_to_directory(tmp_path: pathlib.Path) -> None:
    dir_path: pathlib.Path = tmp_path / "dir"
    dir_path.mkdir()
    fo: FileObject = FileObject(str(dir_path))
    with pytest.raises(OSError):
        fo.write_object({"a":1})


def test_read_object_with_extra_bytes_returns_obj(tmp_path: pathlib.Path) -> None:
    path: pathlib.Path = tmp_path / "extra.pkl"
    obj: Dict[str, int] = {"a": 1}
    data: bytes = pickle.dumps(obj) + b"extradata"
    path.write_bytes(data)
    fo: FileObject = FileObject(str(path))
    # Implementation loads object ignoring trailing data
    assert fo.read_object() == obj


def test_read_bytes_large_file(tmp_path: pathlib.Path) -> None:
    path: pathlib.Path = tmp_path / "large.bin"
    content: bytes = os.urandom(2_000_000)
    path.write_bytes(content)
    fo: FileObject = FileObject(str(path))
    assert fo.read_bytes() == content


@pytest.mark.skipif(sys.platform == "win32", reason="Needs symlink privileges on Windows")
def test_symlink_and_readonly(tmp_path: pathlib.Path) -> None:
    real: pathlib.Path = tmp_path / "real.txt"
    real.write_bytes(b"data")
    link: pathlib.Path = tmp_path / "link.txt"
    os.symlink(real, link)
    fo_link: FileObject = FileObject(str(link))
    assert fo_link.read_bytes() == b"data"

    ro: pathlib.Path = tmp_path / "ro.txt"
    ro.write_text("ro")
    ro.chmod(0o444)
    fo_ro: FileObject = FileObject(str(ro))
    fo_ro.remove()
    assert not ro.exists()


def test_touch_errors(tmp_path: pathlib.Path) -> None:
    path: pathlib.Path = tmp_path / "no" / "dir" / "file"
    fo: FileObject = FileObject(str(path))
    with pytest.raises(FileNotFoundError):
        fo.touch()


def test_unicode_filename(tmp_path: pathlib.Path) -> None:
    path: pathlib.Path = tmp_path / "unicodé.txt"
    fo: FileObject = FileObject(str(path))
    fo.touch()
    data: bytes = "hällo".encode('utf-8')
    fo.write_bytes(data)
    assert fo.read_bytes() == data
