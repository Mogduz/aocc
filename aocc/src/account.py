import os
import sys
from pathlib import Path
from aocc.src.dottedstorage import DottedStorage
from aocc.src.fileobject import FileObject
from aocc.src.cryptoobject import CryptoObject
import keyring
import uuid

class Account:

    if sys.platform.lower() == 'win32':
        _accounts_path: str = f'{os.path.expanduser("~")}/AppData/Local/aocc/accounts'

    def __init__(self, id: str | None = None) -> None:
        self._account_data: DottedStorage = DottedStorage()
        self._id: None = None
        if isinstance(id, str):
            self.set_id(id=id)
            self.load()
            
    def set_id(self, id: str) -> None:
        self._id: str = id

    def load(self) -> None:
        if self._id != None:
            self._account_file: FileObject = FileObject(path=f'{self._accounts_path}/{self._id}')
            crypt_object = self._create_crypto_object()
            if self._account_file.exists() and self._account_file.is_file:
                enc_raw_data: bytes = self._account_file.read_bytes()
                account_data: dict = crypt_object.decrypt_object(enc_obj=enc_raw_data)
                self._account_data.load_data(data=account_data)

    def create(self, username: str, host: str) -> None:
        if self._id == None:
            self._id: str = uuid.uuid4().__str__()
            self._account_file: FileObject = FileObject(path=f'{self._accounts_path}/{self._id}')
            if not self._account_file.exists():
                self._account_file.touch()

            data={
                'id': self._id,
                'user': {
                    'name': username
                },
                'token': {
                    'access': {
                        'data': None,
                        'request_time': None
                    },
                    'refresh': {
                        'data': None,
                        'request_time': None
                    },
                },
                'server': {
                    'host': host,
                    'ip': None,
                    'version': None
                }
            }
            crypt_object = self._create_crypto_object()
            self._account_data.load_data(data=data)
            dump_data: bytes = crypt_object.encrypt_object(obj=self._account_data.get_data())
            self._account_file.write_bytes(data=dump_data)

        return None

    def _create_crypto_object(self) -> CryptoObject | None:
        account_password: str = keyring.get_password(service_name='aocc_accounts', username=self._id)
        account_salt: str = keyring.get_password(service_name='aocc_accounts_salts', username=self._id)
        if account_password != None and account_salt != None:
            return CryptoObject(salt=account_salt, password=account_password)
        return None

    @property
    def id(self) -> str:
        if self._account_data.loaded:
            return self._account_data.get(key='id', default=str())
        return str()

    @property
    def refreshToken(self) -> str:
        if self._account_data.loaded:
            return self._account_data.get(key='token.refresh.data', default=str())
        return str()
    
    @property
    def refreshTokenRequestTime(self) -> float:
        if self._account_data.loaded:
            return self._account_data.get(key='token.refresh.request_time', default=0.0)
        return 0.0

    @property
    def accessToken(self) -> str:
        if self._account_data.loaded:
            return self._account_data.get(key='token.access.data', default=str())
        return str()
    
    @property
    def accessTokenRequestTime(self) -> float:
        if self._account_data.loaded:
            return self._account_data.get(key='token.access.request_time', default=0.0)
        return 0.0
    
    @property
    def userName(self) -> str:
        if self._account_data.loaded:
            return self._account_data.get(key='user.name', default=str())
        return str()