"""install_autostart.py orqali yoqilgan avtomatik ishga tushirishni
o'chiradi.

Ishga tushirish:
    python uninstall_autostart.py
"""

import os
from pathlib import Path

STARTUP_DIR = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
VBS_PATH = STARTUP_DIR / "hey_computer_assistant.vbs"


def main():
    if VBS_PATH.exists():
        VBS_PATH.unlink()
        print("Автозапуск отключён.")
    else:
        print("Автозапуск не найден - возможно, уже был отключён.")


if __name__ == "__main__":
    main()
