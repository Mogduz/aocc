import sys
from PyInstaller.__main__ import run

if __name__ == "__main__":
    # Argumente so, als würdest du sie in der CLI angeben
    args = [
        '--onefile',
        '--name', 'MyApp',
        '--add-data', 'src/my_app/resources;resources',
        'src/my_app/main.py'
    ]
    run(args)