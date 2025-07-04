import sys
from PyInstaller.__main__ import run

if __name__ == "__main__":
    # Argumente so, als würdest du sie in der CLI angeben
    args = [
        '--onedir',
        '--windowed',
        '--name', 'AoCC',
        '--icon=./aocc/src/app_icon.ico'
        '--add-data', './aocc/src/app_icon.ico;src/app_icon.ico',
        './run.py'
    ]
    run(args)