import sys
from PyInstaller.__main__ import run
import os
from pathlib import Path
import shutil

icon_file: Path = Path(f'{os.getcwd()}/aocc/app_icon.ico')
app_info_file: Path = Path(f'{os.getcwd()}/appinfo.yaml')
src_path: Path = Path(f'{os.getcwd()}/aocc/src')
templates_path: Path = Path(f'{os.getcwd()}/aocc/templates')

if __name__ == "__main__":
    if 'dist' in os.listdir(os.getcwd()):
        shutil.rmtree(Path(f'{os.getcwd()}/dist').as_posix())
    # Argumente so, als würdest du sie in der CLI angeben
    args = [
        '--onedir',
        #'--windowed',
        '--name', 'AoCC',
        f'--icon={icon_file.as_posix()}',
        '--add-data', f'{icon_file.as_posix()};.',
        '--add-data', f'{src_path.as_posix()};src',
        '--add-data', f'{templates_path.as_posix()};templates',
        '--add-data', f'{app_info_file.as_posix()};.',
        './run.py'
    ]
    run(args)