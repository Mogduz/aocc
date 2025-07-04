from src.trayicon import TrayIcon
from time import sleep

class Application:

    def __init__(self):
        self.is_running: bool = True
        self.tray_icon: TrayIcon = TrayIcon(icon_path='./src/images/app_icon.ico', name='testTrayApp')
        self.tray_icon.set_exit_callback(callback=self.exit_function)
        self.tray_icon.run()
        print('start running')
        while self.is_running:
            sleep(0.5)
        print('stop running')


    def exit_function(self) -> None:
        print('set running Flag to False')
        self.is_running: bool = False