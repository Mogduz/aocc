import pickle
import pytest
import string

from cryptography.fernet import InvalidToken
from aocc.src.cryptoobject import CryptoObject


def test_encrypt_decrypt_simple_objects():
    salt = "testsalt"
    password = "testpass"
    co = CryptoObject(salt=salt, password=password)
    for obj in [123, "string", [1, 2, 3], {"a": 1, "b": [2, 3]}]:
        encrypted = co.encrypt_object(obj)
        assert isinstance(encrypted, bytes)
        # encrypted should not contain plaintext pickle bytes
        assert pickle.dumps(obj) not in encrypted

        decrypted = co.decrypt_object(encrypted)
        assert decrypted == obj


def test_decrypt_with_wrong_key_raises():
    salt = "testsalt"
    co1 = CryptoObject(salt=salt, password="pass1")
    co2 = CryptoObject(salt=salt, password="pass2")

    obj = {"secret": True}
    enc = co1.encrypt_object(obj)
    with pytest.raises(InvalidToken):
        co2.decrypt_object(enc)


def test_generate_random_secret_default_and_size():
    # Default secret length
    sec = CryptoObject.genereate_random_secret()
    assert isinstance(sec, str)
    assert len(sec) == 32

    # Custom size
    sec16 = CryptoObject.genereate_random_secret(size=16)
    assert len(sec16) == 16
    sec0 = CryptoObject.genereate_random_secret(size=0)
    assert sec0 == ""


def test_generate_random_secret_characters_and_shuffle_usage(monkeypatch):
    # Monkeypatch shuffle_string to verify it's called when shuffle=True
    called = {}
    def fake_shuffle_string(string, rounds):
        called["ok"] = (string, rounds)
        return "ABC"

    monkeypatch.setattr(CryptoObject, 'shuffle_string', fake_shuffle_string)
    sec = CryptoObject.genereate_random_secret(size=10, shuffle=True, shuffle_rounds=5)
    # shuffle_string should be called with correct args
    alphabet = string.ascii_lowercase + string.digits + string.ascii_uppercase + string.punctuation
    assert called["ok"] == (alphabet, 5)
    # secret characters should only be from 'ABC'
    assert all(ch in "ABC" for ch in sec)


def test_shuffle_string_behavior_and_rounds():
    original = "abcdef"
    # Zero rounds returns original
    out0 = CryptoObject.shuffle_string(string=original, rounds=0)
    assert out0 == original

    # One round returns permutation of same characters
    out1 = CryptoObject.shuffle_string(string=original, rounds=1)
    assert sorted(out1) == sorted(original)
    # Should not be exactly equal in most cases; allow rare equal

    # Two rounds still permutation
    out2 = CryptoObject.shuffle_string(string=original, rounds=2)
    assert sorted(out2) == sorted(original)


def test_shuffle_string_time_sleep_monkeypatched(monkeypatch):
    # Prevent actual sleep calls
    sleep_calls = []
    import time as _time
    monkeypatch.setattr(_time, 'sleep', lambda t: sleep_calls.append(t))

    # Use small alphabet for predictability
    result = CryptoObject.shuffle_string(string="xyz", rounds=3)
    # Expect sleep called for i=0,1,2
    assert sleep_calls == [0.0, 1/100000, 2/100000]
    assert sorted(result) == sorted("xyz")
