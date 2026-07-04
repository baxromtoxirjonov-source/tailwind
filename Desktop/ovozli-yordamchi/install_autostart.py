"""Yordamchini Windows kompyuter yoqilganda/kirganda avtomatik (oynasiz,
terminalsiz) ishga tushiradigan qiladi.

Bir marta ishga tushiring:
    python install_autostart.py

O'chirish uchun:
    python uninstall_autostart.py
"""

import os
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
STARTUP_DIR = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
VBS_PATH = STARTUP_DIR / "hey_computer_assistant.vbs"
SCRIPT_PATH = PROJECT_DIR / "gui_assistant.py"


def _pythonw_path():
    pythonw = Path(sys.executable).with_name("pythonw.exe")
    if pythonw.exists():
        return pythonw
    return Path(sys.executable)


def main():
    pythonw = _pythonw_path()
    vbs_content = (
        'Set objShell = CreateObject("WScript.Shell")\n'
        f'objShell.CurrentDirectory = "{PROJECT_DIR}"\n'
        f'objShell.Run """{pythonw}"" ""{SCRIPT_PATH}""", 0, False\n'
    )
    STARTUP_DIR.mkdir(parents=True, exist_ok=True)
    VBS_PATH.write_text(vbs_content, encoding="utf-8")

    print("Готово! Ассистент теперь будет запускаться автоматически при")
    print("включении/входе в Windows - без терминала и без окна консоли.")
    print(f"\nФайл автозапуска: {VBS_PATH}")
    print("Чтобы отключить: python uninstall_autostart.py")


if __name__ == "__main__":
    main()
