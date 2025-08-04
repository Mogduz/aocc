from aocc.src.service import Service, Connection, Package, Lock
from aocc.src.cryptoobject import CryptoObject
from aocc.src.dottedstorage import DottedStorage
from PIL import Image
import pystray
from pystray import Icon

class TrayIconService(Service):

    def __init__(self, name: str, conn_in: Connection, conn_out: Connection):
        super(TrayIconService, self).__init__(name=name, conn_in=conn_in, conn_out=conn_out)
        self.add_package_callback(subject='get_config', callback=self._handle_config_response)
        self._responses: dict = dict()
        self._responses_lock: Lock = Lock()
        self.start()

    def _run(self) -> None:
        self._init_tray_icon_service()

    def _init_tray_icon_service(self) -> None:

        self._tray_icon = Icon(
            name=self.name,
            icon=self._load_icon(),
            title=self.title,
            menu=pystray.Menu(
                pystray.MenuItem('Öffnen', self.on_open),
                pystray.MenuItem('Beenden', self.on_exit)
            )
        )

    def _handle_config_response(self, response: Package):
        if response.Subject == 'get_config':
            if response.StatusCode == 200:
                with self._responses_lock:
                    self._responses[response.PackageID] = response.Payload

    def _request_config(self) -> None:
        request_id = CryptoObject.genereate_random_secret()
        request: Package = Package(
            sender=self.ServiceName, 
            recipent='MainService', 
            package_type='request', 
            package_id=request_id, 
            subject='get_config'
            )
        self.sendPackage(package=Package)
        while True:
            with self._responses_lock:
                if request_id in self._responses:
                    if isinstance(self._responses[request_id], dict):
                        config_data: dict = self._responses[request_id]
                        del self._responses[request_id]
                        break
        
        