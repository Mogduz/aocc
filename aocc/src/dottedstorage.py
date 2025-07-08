import pickle
import os
from cryptography.fernet import Fernet

class DottedStorage:

    _missing = object()
    
    def __init__(self, data: dict | bytes | None = None) -> None: 
        self._loaded: bool = False
        self._modified: bool = False
        if data != None and isinstance(data, bytes) or isinstance(data, dict):
            self.load_data(data=data)
        else:
            self._store: dict = dict()

    def set(self, key: str, value) -> None:
        """Set a value in the nested dict using a dotted key."""
        parts = key.split('.')
        d = self._store
        for part in parts[:-1]:
            if part not in d or not isinstance(d[part], dict):
                d[part] = {}
            d = d[part]
        d[parts[-1]] = value
        self._modified: bool = True
        return None

    def get(self, key: str, default=None):
        """Get a value from the nested dict using a dotted key."""
        parts = key.split('.')
        d = self._store
        for part in parts[:-1]:
            if part in d and isinstance(d[part], dict):
                d = d[part]
            else:
                return default
        return d.get(parts[-1], default)

    def __getitem__(self, key: str):
        val = self.get(key, DottedStorage._missing)
        if val is DottedStorage._missing:
            raise KeyError(f"Key '{key}' not found")
        return val

    def __setitem__(self, key: str, value):
        self.set(key, value)

    def __repr__(self):
        return repr(self._store)

    def get_data(self) -> dict:
        return self._store

    def load_data(self, data: dict) -> None:
        if not self._loaded and not self._modified:
            self._store: dict = data            
        self._loaded: bool = True

    def reset_modified(self) -> None:
        self._modified: bool = False

    @property
    def loaded(self) -> bool:
        try:
            return self._loaded
        except:
            return False
        
    @property
    def modified(self) -> bool:
        try:
            return self._modified
        except:
            return False