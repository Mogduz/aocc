from multiprocessing.connection import Connection
from aocc.src.connectionhandler import ConnectionHandler
from aocc.src.dottedstorage import DottedStorage
from aocc.src.cryptoobject import CryptoObject
from queue import Queue, Empty
from threading import Thread, Lock
from aocc.src.package import Package
from time import sleep

class Service:

    def __init__(self, name: str, conn_in: Connection, conn_out: Connection, request_callback: callable = None, response_callback: callable = None, config_required: bool = True) -> None:
        self._name: str = name
        self._connection_handler: ConnectionHandler = ConnectionHandler(conn_in=conn_in, conn_out=conn_out, package_callback=self._package_callback)
        self._request_callback: callable = request_callback
        self._response_callback: callable = response_callback
        self._config_required: bool = config_required

        self._responses: dict = dict()
        self._responses_dict_lock: Lock = Lock()

        self._config: DottedStorage = DottedStorage()
        self._is_running: bool = False
        self._is_running_lock: Lock = Lock()

    def start(self) -> None:
        if not self.isRunning:
            with self._is_running_lock:
                self._is_running: bool = True
            self._connection_handler.start()
            if self._config_required:
                self._request_config()
                if not self._config.loaded:
                    raise Exception('Loading config went wrong')

    def stop(self) -> None:
        if self.isRunning:
            with self._is_running_lock:
                self._is_running: bool = False
            self._connection_handler.stop()

    def send_package(self, package: Package) -> None:
        self._connection_handler.send_package(package=package)

    def _package_callback(self, package: Package) -> None:
        thread: Thread = Thread(target=self._handle_package, args=(package,), daemon=True)
        thread.start()

    def _handle_package(self, package: Package) -> None:
        if package.Receipent == self._name:
            match package.PackageType:
                case 'request':
                    if self._request_callback != None:
                        self._request_callback(package)
                case 'response':
                    match package.Subject:
                        case 'stop':
                            self.stop()
                        case 'get_config':
                            with self._responses_dict_lock:
                                self._responses[package.PackageID] = package
                    if self._response_callback != None:
                        if package.Subject not in ['dummy', 'get_config']:
                            self._response_callback(package)        
                case _:
                    response: Package = Package(
                        sender=self._name,
                        recipent=package.Sender,
                        package_type='response',
                        package_id=package.PackageID,
                        subject='unkonwn_package_type',
                        code=501,
                        payload=package
                        )
                    self.send_package(package=response)
        else:        
            response: Package = Package(
                sender=self._name,
                recipent=package.Sender,
                package_type='response',
                package_id=package.PackageID,
                subject='wrong_receipent',
                code=500,
                payload=package
                )
            self.send_package(package=response)

    def _request_config(self) -> None:
        request_id: str = self._generate_request_id()
        request: Package = Package(
                    sender=self._name,
                    recipent='ConfigService',
                    package_type='request',
                    package_id=request_id,
                    subject='get_config'
                )
        self._connection_handler.send_package(package=request)
        while True:
            with self._responses_dict_lock:
                if request_id in self._responses:
                    package: Package = self._responses[request_id]
                    del self._responses[request_id]
                    break
            sleep(0.2)
        if package.StatusCode == 200:
            self._config.load_data(package.Payload)

    def _generate_request_id(self) -> str:
        return CryptoObject.genereate_random_secret()

    @property
    def isRunning(self) -> bool:
        with self._is_running_lock:
            result: bool = self._is_running
        return result