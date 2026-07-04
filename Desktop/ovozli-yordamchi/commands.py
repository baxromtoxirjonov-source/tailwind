"""Yordamchi tushunadigan buyruqlarni matndan aniqlab bajaradigan modul."""

import datetime
import os
import subprocess
import webbrowser
from pathlib import Path

import config

HOME = Path.home()


def _open_app(path):
    try:
        if os.path.isabs(path) and os.path.exists(path):
            subprocess.Popen([path])
        else:
            os.startfile(path)
        return True
    except OSError:
        return False


def _find_file(name):
    name = name.lower()
    for root_name in config.SEARCH_ROOTS:
        root = HOME / root_name
        if not root.exists():
            continue
        for dirpath, _dirnames, filenames in os.walk(root):
            for fname in filenames:
                if name in fname.lower():
                    return Path(dirpath) / fname
    return None


def _change_volume(delta_percent):
    try:
        from ctypes import POINTER, cast

        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    except ImportError:
        return False, "Ovoz boshqaruvi uchun kerakli kutubxonalar o'rnatilmagan"

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    current = volume.GetMasterVolumeLevelScalar()
    new_value = min(1.0, max(0.0, current + delta_percent / 100))
    volume.SetMasterVolumeLevelScalar(new_value, None)
    return True, None


def _change_brightness(delta):
    try:
        import screen_brightness_control as sbc
    except ImportError:
        return False, "Yorqinlik boshqaruvi uchun kerakli kutubxona o'rnatilmagan"

    try:
        current = sbc.get_brightness()[0]
        sbc.set_brightness(max(0, min(100, current + delta)))
        return True, None
    except Exception as exc:  # noqa: BLE001 - real hardware/driver errors vary
        return False, str(exc)


def dispatch(text, speak, listen):
    """Berilgan buyruq matnini aniqlab, mos amalni bajaradi.

    speak(text) - yordamchi javob aytishi uchun
    listen() -> str - tasdiqlash kerak bo'lganda qo'shimcha eshitish uchun
    """
    text = text.lower().strip().replace("‘", "'").replace("’", "'")
    if not text:
        speak("Buyruqni eshitmadim, qaytadan urinib ko'ring")
        return

    # --- Dastur yoki sayt ochish ---
    if "och" in text:
        for name, path in config.APPS.items():
            if name in text:
                if _open_app(path):
                    speak(f"{name} ochildi")
                else:
                    speak(f"{name} ni ocholmadim")
                return

        for name, url in config.SITES.items():
            if name in text:
                webbrowser.open(url)
                speak(f"{name} ochildi")
                return

        for name, folder in config.FOLDERS.items():
            if name in text:
                os.startfile(HOME / folder)
                speak(f"{name} papkasi ochildi")
                return

        if "fayl" in text or "papka" in text:
            words = text.replace("ochib ber", "").replace("ochib", "").replace("och", "")
            words = words.replace("fayl", "").replace("papka", "").replace("ni", "").strip()
            if words:
                found = _find_file(words)
                if found:
                    os.startfile(found)
                    speak(f"{words} topildi va ochildi")
                else:
                    speak(f"{words} nomli fayl topilmadi")
                return

        # Ro'yxatdagi dastur/sayt/papkalarga to'g'ri kelmasa, aytilgan nomni
        # to'g'ridan-to'g'ri veb-sayt sifatida ochishga harakat qilamiz
        # (masalan config.py da yo'q "instagram", "wildberries" va h.k.)
        words = text.replace("ochib ber", "").replace("ochib", "").replace("och", "")
        words = words.replace(" ", "").strip()
        if words:
            webbrowser.open(f"https://{words}.com")
            speak(f"{words} saytini ochishga harakat qildim")
            return

    # --- Fayl/papka qidirish ---
    if "qidir" in text and ("fayl" in text or "papka" in text):
        words = text.split("qidir", 1)[-1]
        words = words.replace("fayl", "").replace("papka", "").replace("ni", "").strip()
        if words:
            found = _find_file(words)
            if found:
                speak(f"{words} topildi: {found.parent}")
                os.startfile(found.parent)
            else:
                speak(f"{words} nomli fayl topilmadi")
            return

    # --- Yangi papka yaratish ---
    if "papka yarat" in text:
        words = text.replace("papka yarat", "").replace("nomli", "").replace("nomida", "").strip()
        folder_name = words if words else "Yangi papka"
        new_path = HOME / "Desktop" / folder_name
        new_path.mkdir(parents=True, exist_ok=True)
        speak(f"{folder_name} papkasi Desktop ichida yaratildi")
        return

    # --- Veb qidiruv ---
    if "qidir" in text:
        query = text.split("qidir", 1)[-1].strip()
        if query:
            webbrowser.open(f"https://www.google.com/search?q={query}")
            speak(f"{query} uchun qidiruv natijalarini ochdim")
        else:
            speak("Nimani qidirishni aytmadingiz")
        return

    # --- Vaqt va sana ---
    if "soat" in text or "vaqt" in text:
        now = datetime.datetime.now().strftime("%H:%M")
        speak(f"Hozir soat {now}")
        return

    if "sana" in text or "bugun" in text:
        today = datetime.datetime.now().strftime("%d.%m.%Y")
        speak(f"Bugun {today}")
        return

    # --- Ovoz balandligi ---
    if "ovoz" in text and any(w in text for w in ("baland", "kuchaytir", "oshir")):
        ok, error = _change_volume(15)
        speak("Ovoz balandlashtirildi" if ok else error)
        return

    if "ovoz" in text and any(w in text for w in ("past", "kamaytir", "tushir")):
        ok, error = _change_volume(-15)
        speak("Ovoz pasaytirildi" if ok else error)
        return

    if "ovoz" in text and "o'chir" in text:
        ok, error = _change_volume(-100)
        speak("Ovoz o'chirildi" if ok else error)
        return

    # --- Ekran yorqinligi ---
    if "yorqinlik" in text and any(w in text for w in ("oshir", "baland", "kuchaytir")):
        ok, error = _change_brightness(15)
        speak("Yorqinlik oshirildi" if ok else error)
        return

    if "yorqinlik" in text and any(w in text for w in ("kamaytir", "past", "tushir")):
        ok, error = _change_brightness(-15)
        speak("Yorqinlik kamaytirildi" if ok else error)
        return

    # --- Kompyuterni o'chirish / qayta yoqish (tasdiqlash talab qilinadi) ---
    if "kompyuter" in text and "o'chir" in text:
        speak("Kompyuterni o'chirishni tasdiqlaysizmi? Ha yoki yo'q deb ayting")
        answer = listen().lower()
        if "ha" in answer:
            speak("Xayr, kompyuter o'chmoqda")
            subprocess.run(["shutdown", "/s", "/t", "5"])
        else:
            speak("Bekor qilindi")
        return

    if "qayta yoq" in text or "restart" in text:
        speak("Kompyuterni qayta yoqishni tasdiqlaysizmi? Ha yoki yo'q deb ayting")
        answer = listen().lower()
        if "ha" in answer:
            speak("Kompyuter qayta yoqilmoqda")
            subprocess.run(["shutdown", "/r", "/t", "5"])
        else:
            speak("Bekor qilindi")
        return

    speak("Kechirasiz, bu buyruqni tushunmadim")
