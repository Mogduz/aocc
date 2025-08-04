from threading import Thread, Lock
from multiprocessing.connection import Connection
from time import sleep
from aocc.src.package import Package

class RouterService:

    def __init__(self, name: str) -> None:
        self._connections: dict = dict()
        self._workers: dict = dict()
        self._connections_lock: Lock = Lock()
        self._workers_lock: Lock = Lock()
        self._running: bool = False
        

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def _run(self) -> None:
        while self._running:
            workers: list = self._get_workers_names()
            services: list = self._get_services_names()
            runs: int = 0
            while True:
                run: bool = False
                for service in services:
                    if service not in workers:
                        self._start_workers(name=service)
                        run: bool = True
                if not run:
                    if runs == 0:
                        sleep(0.2)
                    break
                else:
                    runs += 1

    def add_connection_pair(self, name: str, conn_in: Connection, conn_out: Connection) -> bool:
        with self._connections_lock:
            if name not in self._connections.keys():
                self._connections[name] = {'in': conn_in, 'out': conn_out}
                return True
        return False
    
    def del_connection_pair(self, name: str) -> bool:
        with self._connections_lock:
            if name in self._connections.keys():
                del self._connections[name]
                if name not in self._connections.keys():
                    return True
        return False

    def _start_workers(self, name: str) -> None:
        worker_in: Thread = Thread(target=self._handle_connection_in, args=(name,), daemon=True, name=f'worker_{name}_in')
        worker_out: Thread = Thread(target=self._handle_connection_out, args=(name,), daemon=True, name=f'worker_{name}_out')
        with self._workers_lock:
            self._workers[name] = {'running': True, 'worker_in': worker_in, 'worker_out': worker_out}
            self._workers[name]['worker_in'].start()
            self._workers[name]['worker_out'].start()

    def _get_connection(self, name: str, direction: str) -> Connection | None:
        with self._connections_lock:
            if name in self._connections.keys():
                return self._connections[name][direction]
        return None
    
    def _get_connections(self, names: list, direction: str) -> list:
        result: list = list()
        for name in names:
            connection: Connection = self._get_connection(name=name, direction=direction)
            if isinstance(connection, Connection):
                result.append(connection)

    def _get_services_names(self) -> list:
        with self._connections_lock:
            return list(self._connections.keys())

    def _get_workers_names(self) -> list:
        with self._workers_lock:
            return list(self._workers.keys())

    def _get_worker_running_status(self, worker_name: str) -> bool:
        with self._workers_lock:
            if worker_name in self._workers.keys():
                try:
                    return self._workers[worker_name]['running']
                except:
                    return False
        return False

    def _handle_connection_in(self, name: str) -> None:
        connection: Connection = self._get_connection(name=name, direction='in')
        if isinstance(connection, Connection):
            while self._running and self._get_worker_running_status(worker_name=name):
                try:
                    if connection.poll():
                        package: Package = connection.recv()
                    else:
                        sleep(0.2)
                except:
                    break

    def _handle_connection_out(self, name: str) -> None:
        connection: Connection = self._get_connection(name=name, direction='out')
        if isinstance(connection, Connection):
            while self._running:
                pass

