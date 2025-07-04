import sys
from PyInstaller.__main__ import run
import os
from pathlib import Path

icon_file: Path = Path(f'{os.getcwd()}/aocc/app_icon.ico')

if __name__ == "__main__":
    print(os.getcwd())
    # Argumente so, als würdest du sie in der CLI angeben
    args = [
        '--onedir',
        '--windowed',
        '--name', 'AoCC',
        f'--icon={icon_file.as_posix()}'
        '--add-data', f'{icon_file.as_posix()};app_icon.ico',
        './run.py'
    ]
    run(args)