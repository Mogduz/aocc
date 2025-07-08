import sys
import threading
from PIL import Image
import pystray
from time import sleep

class TrayIconWindows:

    def __init__(self, icon_path, name="TrayApp", title="Tray App"):
        self.icon_path = icon_path
        self.name = name
        self.title = title

        self.open_callback: callable = None
        self.exit_callback: callable = None

        self.icon = pystray.Icon(
            name=self.name,
            icon=self._load_icon(),
            title=self.title,
            menu=pystray.Menu(
                pystray.MenuItem('Öffnen', self.on_open),
                pystray.MenuItem('Beenden', self.on_exit)
            )
        )

    def _load_icon(self) -> any:
        try:
            return Image.open(self.icon_path)
        except Exception as e:
            print('ERROR -> ')
            print(e)
            sleep(10)
            exit(1)

    def on_open(self, icon, item):
        try:
            self.open_callback()
        except Exception as e:
            pass
        print("'Öffnen' ausgewählt")
        # TODO: Hier GUI öffnen oder Funktion aufrufen

    def on_exit(self, icon, item):
        try:
            self.exit_callback()
        except Exception as e:
            pass
        self.icon.stop()


    def set_exit_callback(self, callback: callable) -> None:
        self.exit_callback: callable = callback

    def set_open_callback(self, callback: callable) -> None:
        self.open_callback: callable = callback

    def run(self):
        threading.Thread(target=self.icon.run, daemon=True).start()
