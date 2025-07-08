from pathlib import Path
from aocc.src.dottedstorage import DottedStorage


class Account:

    def __init__(self) -> None:
        self._account_data: DottedStorage = DottedStorage()

    def create(self, username: str, host: str) -> None:
        if not self._account_data.loaded:
            
            self._account_data.load_data(data={
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
            })
        if self._account_data.loaded:
            self._account_data.dump_to_file()
        return None

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