import os
import pickle

class FileObject:

    def __init__(self, path: str) -> None:
        self._path: str = path

    def exists(self) -> bool:
        return os.path.exists(self._path)
    
    def is_file(self) -> bool:
        return os.path.isfile(self._path)
    
    def remove(self) -> None:
        if self.exists() and self.is_file():
            os.unlink(self._path)

    def touch(self):
        with open(file=self._path, mode="a") as file:
            os.utime(self._path, None)

    def read_bytes(self) -> bytes:
        if self.exists() and self.is_file():
            with open(file=self._path, mode='rb') as reader:
                return reader.read()
        return b''
    
    def write_bytes(self, data: bytes) -> int:
        with open(file=self._path, mode='wb') as writer:
            return writer.write(data)
        
    def read_object(self) -> any:
        data: bytes = self.read_bytes()
        if len(data) > 0:
            try:
                return pickle.loads(data)
            except:
                return None
        return None
    
    def write_object(self, obj: any) -> bool:
        data = pickle.dumps(obj)
        if len(data) == self.write_bytes(data=data):
            return True
        return False
        