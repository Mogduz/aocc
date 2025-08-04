from multiprocessing.connection import Connection
from aocc.src.package import Package
from threading import Thread, Lock
from queue import Queue
from time import sleep

class ConnectionHandler:

    def __init__(self, conn_in: Connection, conn_out: Connection, package_callback: callable = None, auto_start: bool = False) -> None:
        self._conn_in: Connection = conn_in
        self._conn_out: Connection = conn_out
        self._callback: callable = package_callback

        self._packages_in: Queue = Queue()
        self._packages_in_queue_lock: Lock = Lock()

        self._packages_out: Queue = Queue()
        self._packages_out_queue_lock: Lock = Lock()

        self._is_running: bool = False
        self._is_running_lock: Lock = Lock()

        if auto_start:
            self.start()

    def start(self) -> None:
        if not self.isRunning:
            with self._is_running_lock:
                self._is_running: bool = True
            Thread(target=self._handle_conn_in, daemon=True).start()
            if self._callback != None:
                Thread(target=self._handle_packages_in, daemon=True).start()
            Thread(target=self._handle_packages_out, daemon=True).start()

    def stop(self) -> None:
        if self.isRunning:
            with self._is_running_lock:
                self._is_running: bool = False

    def _handle_conn_in(self) -> None:
        while self.isRunning:
            if self._conn_in.poll():
                package: Package = self._conn_in.recv()
                with self._packages_in_queue_lock:
                    self._packages_in.put(package)

    def _handle_packages_in(self) -> None:
        while self.isRunning and not self.packagesInEmpty:
            if self._callback != None:
                package: Package | None = self.get_package()
                if package != None:    
                    self._callback(package)
                else:
                    sleep(0.2)
        return None

    def _handle_packages_out(self) -> None:
        while self.isRunning and not self.packagesOutEmpty:
            package: Package | None = self._get_out_package()
            if package != None:
                self._conn_out.send(package)
            else:
                sleep(0.2)
        return None
    
    def _get_out_package(self) -> Package | None:
        try:
            with self._packages_out_queue_lock:
                package: Package = self._packages_out.get(block=False)
        except:
            package: None = None
        finally:
            return package

    def get_package(self) -> Package | None:
        try:
            with self._packages_in_queue_lock:
                package: Package = self._packages_in.get(block=False)
        except:
            package: None = None
        finally:
            return package

    def send_package(self, package: Package) -> None:
        with self._packages_out_queue_lock:
            self._packages_out.put(package)    

    @property
    def packagesInEmpty(self) -> bool:
        try:
            with self._packages_in_queue_lock:
                result: bool = self._packages_in.empty()
            return result
        except:
            return True
        
    @property
    def packagesOutEmpty(self) -> bool:
        try:
            with self._packages_out_queue_lock:
                result: bool = self._packages_out.empty()
            return result
        except:
            return True

    @property
    def isRunning(self) -> bool:
        try:
            with self._is_running_lock:
                result: bool = self._is_running
            return result
        except:
            return False