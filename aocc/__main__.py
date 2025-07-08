import sys
from aocc.application import Application
from time import sleep

def run():
    """
    Wrapper für den Aufruf der main-Funktion aus my_app.core.
    Fängt Ausnahmen ab und gibt einen Fehlercode zurück.

    :return: Exit-Code (0 = Erfolg, >0 = Fehler)
    """
    try:
        Application()
        return 0
    except Exception as e:
        print(f"Fehler: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(run())