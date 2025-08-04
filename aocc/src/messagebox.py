from aocc.src.package import Package
from threading import Lock

class MessageBox:

    def __init__(self, name: str, direction: str) -> None:
        self._name: str = name
        self._direction: str = direction
        self._data: list = list()
        self._data_lock: Lock = Lock()

    def add_package(self, package: Package) -> bool:
        try:
            with self._data_lock:
                self._data.append(package)
            result: bool = True
        except:
            result: bool = False
        finally:
            return result

    def add_packages(self, packages: list) -> bool:
        try:
            with self._data_lock:
                for package in packages:
                    if isinstance(package, Package):
                        self._data.append(package)
            result: bool = True
        except:
            result: bool = False
        finally:
            return result

    def get_package(self, block: bool = True) -> Package:
        if block:
            while True:
                if not self.empty():
                    with self._data_lock:
                        package: Package = self._data.pop(0)
                    break
        else:
            if not self.empty():
                with self._data_lock:
                        package: Package = self._data.pop(0)
            else:
                raise Exception('No Data in list Error')
        return package

    def get_all_packages(self) -> list:
        error: bool = False
        with self._data_lock:
            try:
                result: list = self._data
            except:
                result: list = list()
                error: bool = True
            finally:
                if not error:
                    self._data.clear()
                return result

    def empty(self) -> bool:
        try:
            if self.length() > 0:
                result: bool = False
            elif self.length() == 0:
                result: bool = True
        except:
            result: bool = False
        finally:
            return result

    def length(self) -> int:
        try:
            with self._data_lock:
                length: int = len(self._data)
        except:
            length: int = 0
        finally:
            return length