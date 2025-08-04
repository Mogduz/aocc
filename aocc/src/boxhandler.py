from aocc.src.messagebox import MessageBox
from threading import Lock
from aocc.src.worker import Worker
from aocc.src.package import Package
from time import sleep

class BoxHandler:

    def __init__(self, direction: str):
        self._direction: str = direction
        self._boxes: dict = dict()
        self._boxes_lock: Lock = Lock()

    def addBox(self, name: str) -> bool:
        try:
            with self._boxes_lock:
                if name not in self._boxes.keys():
                    self._boxes[name] = MessageBox(name=name, direction=self._direction)
                if name in self._boxes.keys():
                    result: bool = True
                else:
                    result: bool = False    
        except:
            result: bool = False
        finally:
            return result

    def delBox(self, name: str) -> bool:
        try:
            with self._boxes_lock:
                if name in self._boxes.keys():
                    del self._boxes[name]
                if name not in self._boxes.keys():
                    result: bool = True
                else:
                    result: bool = False
        except:
            result: bool = False
        finally:
            return result
        
    def get_package_from_box(self, name: str, block: bool = False) -> Package:
        worker: Worker = Worker(target=self._get_package, args=(name, block))
        worker.start()
        worker.join()
        while True:
            if worker.finished:
                if isinstance(worker.result, Package):
                    return worker.result
                else:
                    raise Exception('excepted format result format was wrong')
            else:
                sleep(0.2)

    def add_package_to_box(self, name: str, package: Package) -> bool:
        worker: Worker = Worker(target=self._add_package, args=(name, package))
        worker.start()
        worker.join()
        while True:
            if worker.finished:
                return worker.result
            else:
                sleep(0.2)

    def _add_package(self, name: str, package: Package) -> bool:
        box: MessageBox | None = None
        with self._boxes_lock:
            if name in self._boxes.keys():
                box: MessageBox = self._boxes[name]
        if isinstance(box, MessageBox):
            result: bool = box.add_package(package=package)
            return result
        else:
            raise Exception(f'Box named {name} not found')

    def _get_package(self, name: str, block: bool = False) -> Package:
        box: MessageBox | None = None
        with self._boxes_lock:
            if name in self._boxes.keys():
                box: MessageBox = self._boxes[name]
        if isinstance(box, MessageBox):
            package: Package = box.get_package(block=block)
            return package
        else:
            raise Exception(f'Box named {name} not found')