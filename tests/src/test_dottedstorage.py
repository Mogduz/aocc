import pickle
import pytest

from aocc.src.dottedstorage import DottedStorage


def test_init_no_data():
    ds = DottedStorage()
    # Should start with empty store
    assert ds.get_data() == {}
    assert not ds.loaded
    assert not ds.modified


def test_init_with_dict_data():
    data = {'a': 1, 'nested': {'b': 2}}
    ds = DottedStorage(data)
    # Should load provided dict
    assert ds.get_data() is data
    assert ds.loaded
    assert not ds.modified


def test_init_with_bytes_data():
    payload = pickle.dumps({'x': 42})
    ds = DottedStorage(payload)
    # Bytes data should be loaded as raw store
    assert ds.get_data() == payload
    assert ds.loaded
    # Accessing via get on non-dict _store raises AttributeError
    with pytest.raises(AttributeError):
        ds.get('any', 'def')


def test_set_and_get_simple_key():
    ds = DottedStorage()
    ds.set('key', 'value')
    assert ds.get('key') == 'value'
    assert ds['key'] == 'value'
    assert not ds.loaded
    assert ds.modified


def test_set_and_get_nested_key():
    ds = DottedStorage()
    ds.set('a.b.c', 123)
    # Nested retrieval
    assert ds.get('a.b.c') == 123
    # Intermediate mapping created
    assert isinstance(ds.get_data()['a'], dict)
    # Default at intermediate
    assert ds.get('a.b.x', None) is None


def test_overwrite_intermediate_non_dict():
    ds = DottedStorage()
    ds.set('x', 5)
    # Now overwrite x.y, should replace integer 5
    ds.set('x.y', 'z')
    assert ds.get('x.y') == 'z'
    # Original x as scalar should be replaced by dict
    assert isinstance(ds.get_data()['x'], dict)


def test_get_default_behaviour():
    ds = DottedStorage()
    # Non-existing key returns default None
    assert ds.get('foo') is None
    # Custom default
    assert ds.get('foo.bar', default=0) == 0


def test_getitem_missing_raises():
    ds = DottedStorage()
    with pytest.raises(KeyError):
        _ = ds['does.not.exist']


def test_setitem_alias():
    ds = DottedStorage()
    ds['m.n'] = 99
    assert ds.get('m.n') == 99
    assert ds.modified


def test_repr_and_get_data_link():
    ds = DottedStorage()
    ds.set('a', 1)
    # repr should reflect internal store
    assert repr(ds) == repr(ds.get_data())
    # get_data returns direct reference
    store = ds.get_data()
    store['new'] = True
    assert ds.get('new') is True


def test_load_data_only_once():
    initial = {'p': 1}
    ds = DottedStorage(initial)
    # First load sets store
    assert ds.get('p') == 1
    # Mutate and mark modified
    ds.set('q', 2)
    # Attempt to load new data should have no effect
    ds.load_data(data={'x': 9})
    assert ds.get('q') == 2
    assert 'x' not in ds.get_data()


def test_reset_modified_and_properties():
    ds = DottedStorage()
    ds.set('a.b', 5)
    assert ds.modified
    # Reset
    ds.reset_modified()
    assert not ds.modified
    # loaded remains unchanged
    assert not ds.loaded


def test_empty_and_edge_case_keys():
    ds = DottedStorage()
    # Empty key creates entry with empty string
    ds.set('', 'empty')
    assert ds.get('') == 'empty'
    # Trailing dot creates empty part
    ds.set('key.', 'val')
    assert ds.get('key.') == 'val'


def test_modified_flag_on_setitem_and_set():
    ds = DottedStorage()
    assert not ds.modified
    ds.set('a', 1)
    assert ds.modified
    ds.reset_modified()
    ds['b.c'] = 2
    assert ds.modified
