from time import time

class Package:

    def __init__(self, sender: str, recipent: str, package_type: str, package_id: str, subject: str, code: int = 0, payload: any = None):
        self._created: float = time()
        self._sender: str = sender
        self._receipent: str = recipent
        if package_type in ['request', 'response']:
            self._package_type: str = package_type
        else:
            raise Exception('only <request> or <response> as package_type are allowed')
        self._package_id: str = package_id
        self._subject: str = subject
        self._code: int = code
        self._payload: any = payload

    @property
    def Created(self) -> float:
        try:
            return self._created
        except:
            return float(0.0)

    @property
    def Sender(self) -> str:
        try:
            return self._sender
        except:
            return str()
        
    @property
    def Receipent(self) -> str:
        try:
            return self._receipent
        except:
            return str()
        
    @property
    def PackageType(self) -> str:
        try:
            return self._package_type
        except:
            return str()
        
    @property
    def PackageID(self) -> str:
        try:
            return self._package_id
        except:
            return str()

    @property
    def Subject(self) -> str:
        try:
            return self._subject
        except:
            return str()
        
    @property
    def StatusCode(self) -> int:
        try:
            return self._code
        except:
            return int(0)

    @property
    def Payload(self) -> any:
        try:
            return self._payload
        except:
            return None