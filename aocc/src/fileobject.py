import os
import pickle

class FileObject:

    def __init__(self, path: str) -> None:
        self._path: str = path

    def exists(self) -> bool:
        return os.path.exists(self._path)
    
    def is_file(self) -> bool:
        return os.path.isfile(self._path)
    
    def read_bytes(self) -> bytes:
        with open(file=self._path, mode='rb') as reader:
            return reader.read()

    def write_bytes(self, data: bytes) -> int:
        with open(file=self._path, mode='wb') as writer:
            return writer.write(data)
        
    def read_object(self) -> any:
        return pickle.loads(self.read_bytes())
    
    def write_object(self, obj: any) -> bool:
        data = pickle.dumps(obj)
        if len(data) == self.write_bytes(data=data):
            return True
        return False
        