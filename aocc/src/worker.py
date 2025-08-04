from threading import Thread, Lock

class Worker(Thread):

    
    def __init__(self, target: callable, args: tuple, name: str | None = None, daemon: bool = False, **kwargs):
        super().__init__()
        self._target: callable = target
        self.name: str = name
        self._args: tuple = args
        self._kwargs: dict = kwargs
        self.daemon: bool = daemon 
        self._result: any = None
        self._result_lock: Lock = Lock()
        self._finished: bool = False
        self._finished_lock: Lock = Lock()
        self._running: bool = False
        self._running_lock: Lock = Lock()

    def run(self) -> None:
        try:
            with self._running_lock:
                self._running: bool = True
            result: any = self._target(*self._args, **self._kwargs)
        except:
            result: any = None
        finally:
            with self._result_lock:
                self._result = result
            with self._running_lock:
                self._running: bool = False
            with self._finished_lock:
                self._finished: bool = True    

    @property
    def result(self) -> any:
        with self._result_lock:
            result: any = self._result
        return result
    
    @property
    def finished(self) -> bool:
        with self._finished_lock:
            result: bool = self._finished
        return result
    
    @property
    def running(self) -> bool:
        with self._running_lock:
            result: bool = self._running
        return result