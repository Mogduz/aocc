import platform

match platform.system().lower():
    case 'windows':
        from aocc.src.trayicon.windows import TrayIconWindows
        import keyring
    case 'linux':
        pass
    case 'darwin':
        pass

from aocc.src.dottedstorage import DottedStorage
from time import sleep
from pathlib import Path
import os
from yaml import load as yaml_load, Loader as yaml_Loader
import pickle

class Application:

    def __init__(self):
        self.user_home: str = os.path.expanduser('~')
        self.app_info: dict = self.load_app_info()
        
        match platform.system().lower():
            case 'windows':
                self.__init__windows__()
            case 'linux':
                self.__init__linux__()
            case 'darwin':
                self.__init__mac__()
            case _:
                self.__init__unsupported__()

        self.is_running: bool = True
        print('start running')
        while self.is_running:
            sleep(0.5)
        print('stop running')

    def __init__windows__(self) -> None:
        self.application_config_dir: Path = Path(f'{self.user_home}/appData/Local/aocc')
        if not self.application_config_dir.exists():
            os.makedirs(self.application_config_dir.as_posix(), exist_ok=True)

        self.config_file: Path = Path(f'{self.application_config_dir}/client_config.cfg')
        if self.load_config():
            print(self.config.get(key='language.default'))
        
        self.accounts_config_dir: Path = Path(f'{self.application_config_dir}/accounts')
        if not self.accounts_config_dir.exists():
            os.makedirs(self.accounts_config_dir.as_posix(), exist_ok=True)

        self.salt: str = keyring.get_password(service_name=self.appName, username='app_salt')
        if self.salt == None:
            self.salt: str = CryptoHelper.genereate_random_secret(size=256)      
            keyring.set_password(service_name=self.appName, username='app_salt', password=self.salt)

        accounts: list = os.listdir(self.accounts_config_dir.as_posix())

        if len(accounts) == 0:
            print('run first run wizard')
        else:
            for account in accounts:
                pass

        self.tray_icon: TrayIconWindows = TrayIconWindows(icon_path=self.get_absolute_path(realtiv_path='./app_icon.ico'), name=self.appName, title=self.appName)
        self.tray_icon.set_exit_callback(callback=self.exit_function)
        self.tray_icon.run()

    def __init__linux__(self) -> None:
        try:
            raise NotImplementedError()
        except Exception as e:
            self.catch_exception(e=e)

    def __init__mac__(self) -> None:
        try:
            raise NotImplementedError()
        except Exception as e:
            self.catch_exception(e=e)

    def __init__unsupported__(self) -> None:
        try:
            raise NotImplementedError()
        except Exception as e:
            self.catch_exception(e=e)

    def load_app_info(self) -> dict:
        try:
            with open(file=self.get_absolute_path(realtiv_path='./appinfo.yaml'), mode='rb') as reader:
                appinfo: any = yaml_load(stream=reader.read(), Loader=yaml_Loader)
                if isinstance(appinfo, dict):
                    return appinfo
                raise Exception('Loaded appinfo.yaml data can\'t convert into dict. exit')
        except Exception as e:
            self.catch_exception(e=e)            

    def catch_exception(self, e: Exception) -> None:
        print('ERROR -> ')
        print(e)
        sleep(10)
        exit(1)

    def get_absolute_path(self, realtiv_path: str) -> str:
        if realtiv_path.startswith('./'):
            realtiv_path: str = realtiv_path[2:]
        return Path(f'{os.getcwd()}/_internal/{realtiv_path}').as_posix()

    def write_sample_config(self) -> None:
        from aocc.templates.config import data
        with open(file=self.config_file.as_posix(), mode='wb') as writer:
            writer.write(pickle.dumps(data))

    def exit_function(self) -> None:
        print('set running Flag to False')
        self.is_running: bool = False

    def load_config(self) -> bool:
        try:
            if self.config_file.exists():
                self.config: DottedStorage = DottedStorage(file=self.config_file.as_posix())
                return True
            else:
                from aocc.templates.config import data as config_template_data
                raw_data: bytes = pickle.dumps(config_template_data)
                self.config: DottedStorage = DottedStorage(data=raw_data)
                return self.dump_config()
        except Exception as e:
            return False

    def dump_config(self) -> bool:
        try:
            self.config.dump_to_file(file=self.config_file.as_posix())
            return True
        except Exception as e:
            return False

    @property
    def appName(self) -> str:
        try: 
            return self.app_info['appName']
        except:
            return str()
