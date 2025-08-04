import os
import time
import pytest
from pathlib import Path
import pickle
import keyring

from aocc.src.account import Account

# DummyCrypto stub to bypass encryption
class DummyCrypto:
    def encrypt_object(self, obj):
        return pickle.dumps(obj)
    def decrypt_object(self, enc_obj):
        return pickle.loads(enc_obj)

@pytest.fixture(autouse=True)
def isolate_env(tmp_path, monkeypatch):
    accounts_dir = tmp_path / 'accounts'
    accounts_dir.mkdir()
    # Set isolated accounts path and stub keyring and crypto
    monkeypatch.setattr(Account, '_accounts_path', str(accounts_dir))
    monkeypatch.setattr(keyring, 'get_password', lambda s, u: 'pwd')
    monkeypatch.setattr(keyring, 'set_password', lambda s, u, p: None)
    monkeypatch.setattr(Account, '_create_crypto_object', lambda self: DummyCrypto())
    return accounts_dir

# 1. Kernfunktionalität (Happy Path)
@pytest.mark.parametrize('username,host', [(f'user{i}', f'host{i}') for i in range(1,21)],
                         ids=[f'valid_input_{i}' for i in range(1,21)])
def test_create_returnsExpectedResult_forValidInput(username, host):
    '''Happy path: valid username/host'''
    acc = Account()
    acc.create(username, host)
    acc2 = Account(acc.id)
    assert acc2.id == acc.id
    assert acc2.userName == username

# 2. Grenz- und Eckfälle
boundary_names = [
    '', 'u', 'u'*10, 'u'*31, 'u'*63, 'u'*64, 'u'*127, 'u'*128,
    'u'*255, 'u'*256, 'u'*512, 'u'*1024,
    ' ', '   ', '用户', '!', '123', 'a1b2', '_', '-'
]
@pytest.mark.parametrize('name', boundary_names,
                         ids=[f'username_len_{len(name)}' for name in boundary_names])
def test_boundary_username_cases(name):
    '''Boundary cases for username'''
    acc = Account()
    acc.create(name, 'host')
    acc2 = Account(acc.id)
    assert acc2.userName == name

# 3. Fehler- und Ausnahmebehandlung
invalid_usernames = [None, 123, ['a'], {'u':'a'}, 1.23, True, (1,2), b'bytes']
unserializable = lambda x: x

@pytest.mark.parametrize('invalid_username', invalid_usernames,
                         ids=[f'invalid_username_{i}' for i in range(len(invalid_usernames))])
def test_error_nonstring_but_serializable(invalid_username):
    '''Non-string serializable types are stored and retrievable'''
    acc = Account()
    acc.create(invalid_username, 'host')
    acc2 = Account(acc.id)
    assert acc2.userName == invalid_username

@pytest.mark.parametrize('bad', [unserializable], ids=['lambda_unserializable'])
def test_error_unserializable_username_raises(bad):
    '''Unserializable data in username raises PicklingError'''
    acc = Account()
    with pytest.raises(pickle.PicklingError):
        acc.create(bad, 'host')

# 4. Seiteneffekte und Zustandsänderungen
@pytest.mark.parametrize('i', range(1,21), ids=[f'file_creation_{i}' for i in range(1,21)])
def test_side_effect_file_created_on_create(i):
    '''File created on create call'''
    acc = Account()
    acc.create(f'user{i}', 'host')
    file_path = Path(Account._accounts_path, acc.id)
    assert file_path.exists() and file_path.is_file()

# 5. Abhängigkeiten isolieren (Mocks/Stubs)
@pytest.mark.parametrize('i', range(1,21), ids=[f'mock_crypto_call_{i}' for i in range(1,21)])
def test_mock_create_crypto_called(i, monkeypatch):
    '''_create_crypto_object invoked exactly once per create'''
    calls = {'count': 0}
    def fake(self):
        calls['count'] += 1
        return DummyCrypto()
    monkeypatch.setattr(Account, '_create_crypto_object', fake)
    acc = Account()
    acc.create('user', 'host')
    assert calls['count'] == 1

# 6. Determinismus und Performance
@pytest.mark.parametrize('i', range(1,21), ids=[f'perf_create_{i}' for i in range(1,21)])
def test_performance_create(i):
    '''create() completes within threshold'''
    acc = Account()
    start = time.time()
    acc.create('perf', 'test')
    assert time.time() - start < 0.05

# 7. Teststruktur und Best Practices Teststruktur und Best Practices
@pytest.mark.parametrize('i', range(1,21), ids=[f'structure_isolation_{i}' for i in range(1,21)])
def test_structure_isolation(i, isolate_env):
    '''Isolated env per test'''
    acc = Account()
    acc.create('u', 'h')
    assert Account._accounts_path.endswith('accounts')
