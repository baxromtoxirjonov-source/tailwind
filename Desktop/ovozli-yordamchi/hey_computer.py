"""Hey Computer — ovozli AI yordamchi (Windows). Barcha kod bitta faylda.

Ishga tushirish:
    python hey_computer.py

Windows yoqilganda/kirganda avtomatik (oynasiz) ishga tushirish:
    python hey_computer.py --install-autostart
Avtomatik ishga tushirishni o'chirish:
    python hey_computer.py --uninstall-autostart

Kerakli kutubxonalar (bir marta o'rnatiladi):
    pip install SpeechRecognition PyAudio pyttsx3 pycaw comtypes screen-brightness-control anthropic

Claude AI orqali erkin (ruscha) suhbat va "aqlli" tushunish uchun
ANTHROPIC_API_KEY muhit o'zgaruvchisini o'rnating (https://console.anthropic.com).
O'rnatilmasa, yordamchi qat'iy o'zbekcha kalit-so'zlar bilan ishlayveradi
(pastdagi DISPATCH bo'limiga qarang).
"""

import ctypes
import datetime
import os
import queue
import subprocess
import sys
import threading
import time
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import font as tkfont

import anthropic
import pyttsx3
import speech_recognition as sr

HOME = Path.home()

# ============================================================
#  SOZLAMALAR — bu yerni o'zgartirasiz
# ============================================================

# Uyg'otuvchi so'z (shu so'zlardan birini aytsangiz, yordamchi buyruqni
# kuta boshlaydi)
WAKE_WORDS = ["компьютер", "эй компьютер", "хей компьютер", "привет компьютер"]

# Nutqni tanish tili. Ruscha gapirish uchun "ru-RU" qo'yilgan.
#
# MUHIM: quyidagi DISPATCH funksiyasidagi kalit so'zli (qat'iy) buyruq
# tanish tizimi lotin-o'zbekcha yozilgan ("och", "qidir", "papka"...) va
# shuning uchun ru-RU tanish natijasi bilan mos kelmaydi. Bu muammo emas,
# chunki AI yoqilgan bo'lsa (ANTHROPIC_API_KEY o'rnatilgan bo'lsa) barcha
# buyruqlar AI orqali - matnning qaysi tilda bo'lishidan qat'iy nazar -
# tushuniladi. DISPATCH faqat AI o'rnatilmagan hollarda zaxira sifatida
# ishlaydi (o'sha holda o'zbekcha gapirish kerak bo'ladi).
LANGUAGE = "ru-RU"

# Ovoz bilan ochsa bo'ladigan dasturlar. Kalit - buyruqda aytiladigan nom,
# qiymat - dastur fayli (agar PATH'da bo'lmasa to'liq yo'l ko'rsating).
APPS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "brauzer": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "notepad": "notepad.exe",
    "bloknot": "notepad.exe",
    "explorer": "explorer.exe",
    "fayllar": "explorer.exe",
    "calculator": "calc.exe",
    "kalkulyator": "calc.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
}

# Ovoz bilan ochsa bo'ladigan saytlar
SITES = {
    "youtube": "https://youtube.com",
    "google": "https://google.com",
    "gmail": "https://mail.google.com",
    "telegram": "https://web.telegram.org",
    "instagram": "https://instagram.com",
}

# Ovoz bilan ochsa/qidirsa bo'ladigan papkalar (foydalanuvchi papkasiga nisbatan)
FOLDERS = {
    "desktop": "Desktop",
    "stol": "Desktop",
    "downloads": "Downloads",
    "yuklab olinganlar": "Downloads",
    "documents": "Documents",
    "hujjatlar": "Documents",
}

# Fayl qidiruvi shu papkalar ichida amalga oshiriladi (ko'p fayl bo'lgan
# joylarni qidirish sekin bo'lgani uchun cheklangan)
SEARCH_ROOTS = ["Desktop", "Downloads", "Documents"]

# --- AI orqali tushunish (ixtiyoriy) ---
# Buyruqni qat'iy kalit so'zlar o'rniga Claude AI yordamida tushunish uchun
# ANTHROPIC_API_KEY muhit o'zgaruvchisini o'rnatish kerak (console.anthropic.com
# dan olinadi). Bu pullik - har bir buyruq uchun kichik summa yechiladi.
#
# Standart model eng qobiliyatli model (claude-opus-4-8). Bu ovozli buyruqlarni
# tez-tez, kichik va sodda so'rovlar bilan aniqlaydigan vazifa bo'lgani uchun,
# tezlik/narx muhimroq bo'lsa, quyidagini "claude-haiku-4-5" ga almashtirishingiz
# mumkin - sifat farqi bu oddiy buyruqlar uchun deyarli sezilmaydi.
AI_MODEL = "claude-opus-4-8"


# ============================================================
#  UYG'OTUVCHI SO'ZNI ANIQLASH
# ============================================================

def wake_word_detected(heard_lower, wake_words):
    # Tasodifiy shovqin ichida uchraydigan qism-so'zlarni chalg'ib
    # ketmasligi uchun butun so'z sifatida tekshiradi.
    tokens = heard_lower.split()
    for phrase in wake_words:
        phrase_tokens = phrase.split()
        n = len(phrase_tokens)
        for i in range(len(tokens) - n + 1):
            if tokens[i:i + n] == phrase_tokens:
                return True
    return False


# ============================================================
#  OVOZ (TTS) TANLASH
# ============================================================

LANG_NAME_HINTS = {
    "ru": ("russian",),
    "uz": ("uzbek",),
    "en": ("english",),
}

FEMALE_HINTS = ("zira", "female", "ayol", "hazel", "susan", "eva")


def configure_voice(tts_engine):
    """Avval nutqni tanish tiliga (LANGUAGE) mos ovoz, topilmasa ayol
    ovozi, u ham bo'lmasa standart ovoz tanlanadi."""
    voices = tts_engine.getProperty("voices")
    lang_prefix = LANGUAGE.split("-")[0].lower()
    name_hints = LANG_NAME_HINTS.get(lang_prefix, (lang_prefix,))

    for voice in voices:
        name = (voice.name or "").lower()
        langs = [str(lang).lower() for lang in getattr(voice, "languages", [])]
        if any(hint in name for hint in name_hints) or any(lang_prefix in lang for lang in langs):
            tts_engine.setProperty("voice", voice.id)
            return

    for voice in voices:
        name = (voice.name or "").lower()
        gender = str(getattr(voice, "gender", "") or "").lower()
        if "female" in gender or any(hint in name for hint in FEMALE_HINTS):
            tts_engine.setProperty("voice", voice.id)
            return

    # Hech qanday moslik topilmasa, standart ovoz qoladi - matn baribir
    # to'g'ri tilda bo'ladi, faqat talaffuz aksenti boshqacha bo'lishi mumkin.


# ============================================================
#  BUYRUQLARNI BAJARISH (kalit-so'z asosidagi zaxira rejim)
# ============================================================

def open_app(path):
    try:
        if os.path.isabs(path) and os.path.exists(path):
            subprocess.Popen([path])
        else:
            os.startfile(path)
        return True
    except OSError:
        return False


def find_file(name):
    name = name.lower()
    for root_name in SEARCH_ROOTS:
        root = HOME / root_name
        if not root.exists():
            continue
        for dirpath, _dirnames, filenames in os.walk(root):
            for fname in filenames:
                if name in fname.lower():
                    return Path(dirpath) / fname
    return None


def change_volume(delta_percent):
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


def change_brightness(delta):
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
    """Berilgan buyruq matnini aniqlab, mos amalni bajaradi (o'zbekcha,
    qat'iy kalit-so'zli zaxira rejim - AI o'rnatilmaganda ishlaydi).

    speak(text) - yordamchi javob aytishi uchun
    listen() -> str - tasdiqlash kerak bo'lganda qo'shimcha eshitish uchun
    """
    text = text.lower().strip().replace("‘", "'").replace("’", "'")
    if not text:
        speak("Buyruqni eshitmadim, qaytadan urinib ko'ring")
        return

    # --- Dastur yoki sayt ochish ---
    if "och" in text:
        for name, path in APPS.items():
            if name in text:
                if open_app(path):
                    speak(f"{name} ochildi")
                else:
                    speak(f"{name} ni ocholmadim")
                return

        for name, url in SITES.items():
            if name in text:
                webbrowser.open(url)
                speak(f"{name} ochildi")
                return

        for name, folder in FOLDERS.items():
            if name in text:
                os.startfile(HOME / folder)
                speak(f"{name} papkasi ochildi")
                return

        if "fayl" in text or "papka" in text:
            words = text.replace("ochib ber", "").replace("ochib", "").replace("och", "")
            words = words.replace("fayl", "").replace("papka", "").replace("ni", "").strip()
            if words:
                found = find_file(words)
                if found:
                    os.startfile(found)
                    speak(f"{words} topildi va ochildi")
                else:
                    speak(f"{words} nomli fayl topilmadi")
                return

        # Ro'yxatdagi dastur/sayt/papkalarga to'g'ri kelmasa, aytilgan nomni
        # to'g'ridan-to'g'ri veb-sayt sifatida ochishga harakat qilamiz
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
            found = find_file(words)
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
        ok, error = change_volume(15)
        speak("Ovoz balandlashtirildi" if ok else error)
        return

    if "ovoz" in text and any(w in text for w in ("past", "kamaytir", "tushir")):
        ok, error = change_volume(-15)
        speak("Ovoz pasaytirildi" if ok else error)
        return

    if "ovoz" in text and "o'chir" in text:
        ok, error = change_volume(-100)
        speak("Ovoz o'chirildi" if ok else error)
        return

    # --- Ekran yorqinligi ---
    if "yorqinlik" in text and any(w in text for w in ("oshir", "baland", "kuchaytir")):
        ok, error = change_brightness(15)
        speak("Yorqinlik oshirildi" if ok else error)
        return

    if "yorqinlik" in text and any(w in text for w in ("kamaytir", "past", "tushir")):
        ok, error = change_brightness(-15)
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


# ============================================================
#  CLAUDE AI ORQALI TUSHUNISH VA RUSCHA SUHBAT (ixtiyoriy)
# ============================================================

AI_TOOLS = [
    {
        "name": "open_app",
        "description": "Открыть программу на компьютере (например Chrome, Notepad, калькулятор, Word, Excel).",
        "input_schema": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "Название программы"}},
            "required": ["name"],
        },
    },
    {
        "name": "open_site",
        "description": "Открыть сайт в браузере (например YouTube, Google, Instagram, Gmail, или любой другой сайт).",
        "input_schema": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "Название сайта"}},
            "required": ["name"],
        },
    },
    {
        "name": "open_folder",
        "description": "Открыть папку на компьютере (Desktop, Downloads, Documents).",
        "input_schema": {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        },
    },
    {
        "name": "find_file",
        "description": "Найти файл на компьютере и открыть его.",
        "input_schema": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "Имя файла или его часть"}},
            "required": ["name"],
        },
    },
    {
        "name": "create_folder",
        "description": "Создать новую папку на рабочем столе.",
        "input_schema": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "Имя новой папки"}},
            "required": ["name"],
        },
    },
    {
        "name": "web_search",
        "description": "Найти что-либо в Google.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "get_time",
        "description": "Сказать текущее время.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_date",
        "description": "Сказать сегодняшнюю дату.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "volume_control",
        "description": "Увеличить, уменьшить или выключить громкость звука.",
        "input_schema": {
            "type": "object",
            "properties": {"direction": {"type": "string", "enum": ["up", "down", "mute"]}},
            "required": ["direction"],
        },
    },
    {
        "name": "brightness_control",
        "description": "Увеличить или уменьшить яркость экрана.",
        "input_schema": {
            "type": "object",
            "properties": {"direction": {"type": "string", "enum": ["up", "down"]}},
            "required": ["direction"],
        },
    },
    {
        "name": "shutdown_computer",
        "description": "Выключить компьютер. Всегда требует отдельного подтверждения пользователя.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "restart_computer",
        "description": "Перезагрузить компьютер. Всегда требует отдельного подтверждения пользователя.",
        "input_schema": {"type": "object", "properties": {}},
    },
]

AI_SYSTEM_PROMPT = (
    "Ты — голосовой ассистент на личном компьютере пользователя. "
    "Отвечай всегда на русском языке, кратко и по-разговорному, без длинных "
    "списков и заголовков. Если сказанное подходит под одно из доступных "
    "действий (tools) — вызови его. Если это обычный разговор, приветствие "
    "или вопрос, на который не нужно действие компьютера — просто ответь "
    "текстом, как в обычной беседе."
)

AI_MAX_HISTORY_MESSAGES = 20

_ai_history = []


def ai_is_configured():
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def ai_handle(text, speak, listen):
    """Matnni Claude'ga suhbat tarixi bilan yuboradi: tanlagan vositasini
    bajaradi yoki oddiy matn javobini o'qib beradi. Suhbat tarixi keyingi
    chaqiruvlar uchun saqlanadi."""
    client = anthropic.Anthropic()
    _ai_history.append({"role": "user", "content": text})

    response = client.messages.create(
        model=AI_MODEL,
        max_tokens=300,
        system=AI_SYSTEM_PROMPT,
        tools=AI_TOOLS,
        messages=_ai_history,
    )

    tool_use = next((block for block in response.content if block.type == "tool_use"), None)
    if tool_use is None:
        reply = "".join(block.text for block in response.content if block.type == "text").strip()
        reply = reply or "Не понял, повторите, пожалуйста"
        _ai_history.append({"role": "assistant", "content": reply})
        speak(reply)
        _ai_trim_history()
        return

    _ai_history.append({"role": "assistant", "content": response.content})
    result_summary = _ai_run_tool(tool_use.name, tool_use.input or {}, speak, listen)
    _ai_history.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": result_summary,
                }
            ],
        }
    )
    _ai_trim_history()


def _ai_trim_history():
    # Uzoq suhbatda xabarlar cheksiz ko'payib ketmasligi uchun oxirgi
    # N ta xabarni saqlaymiz.
    if len(_ai_history) > AI_MAX_HISTORY_MESSAGES:
        del _ai_history[: len(_ai_history) - AI_MAX_HISTORY_MESSAGES]


def _ai_match(name, mapping):
    name = (name or "").lower()
    for key in mapping:
        if key in name or name in key:
            return key
    return None


def _ai_run_tool(name, args, speak, listen):
    """Vositani bajaradi, ovoz bilan javob beradi va Claude uchun qisqa
    natija matnini qaytaradi (suhbat tarixiga yozish uchun)."""

    if name == "open_app":
        match = _ai_match(args.get("name"), APPS)
        if match and open_app(APPS[match]):
            speak(f"Открываю {match}")
            return f"Открыл {match}"
        speak(f"Не нашёл программу {args.get('name')}")
        return "Программа не найдена"

    if name == "open_site":
        raw_name = (args.get("name") or "").strip()
        match = _ai_match(raw_name, SITES)
        if match:
            webbrowser.open(SITES[match])
            speak(f"Открываю {match}")
            return f"Открыл сайт {match}"
        guess = raw_name.lower().replace(" ", "")
        webbrowser.open(f"https://{guess}.com")
        speak(f"Пытаюсь открыть сайт {guess}")
        return f"Попытался открыть {guess}.com"

    if name == "open_folder":
        match = _ai_match(args.get("name"), FOLDERS)
        if match:
            os.startfile(HOME / FOLDERS[match])
            speak(f"Открыл папку {match}")
            return f"Открыл папку {match}"
        speak(f"Не нашёл папку {args.get('name')}")
        return "Папка не найдена"

    if name == "find_file":
        found = find_file(args.get("name", ""))
        if found:
            os.startfile(found)
            speak(f"Нашёл {args.get('name')} и открыл")
            return f"Файл найден и открыт: {found}"
        speak(f"Файл {args.get('name')} не найден")
        return "Файл не найден"

    if name == "create_folder":
        folder_name = args.get("name") or "Новая папка"
        new_path = HOME / "Desktop" / folder_name
        new_path.mkdir(parents=True, exist_ok=True)
        speak(f"Папка {folder_name} создана на рабочем столе")
        return f"Папка {folder_name} создана"

    if name == "web_search":
        query = args.get("query", "")
        webbrowser.open(f"https://www.google.com/search?q={query}")
        speak(f"Открыл результаты поиска по запросу {query}")
        return f"Поиск выполнен: {query}"

    if name == "get_time":
        now = datetime.datetime.now().strftime("%H:%M")
        speak(f"Сейчас {now}")
        return f"Время: {now}"

    if name == "get_date":
        today = datetime.datetime.now().strftime("%d.%m.%Y")
        speak(f"Сегодня {today}")
        return f"Дата: {today}"

    if name == "volume_control":
        delta = {"up": 15, "down": -15, "mute": -100}.get(args.get("direction"), 0)
        ok, error = change_volume(delta)
        speak("Готово" if ok else error)
        return "Громкость изменена" if ok else str(error)

    if name == "brightness_control":
        delta = {"up": 15, "down": -15}.get(args.get("direction"), 0)
        ok, error = change_brightness(delta)
        speak("Готово" if ok else error)
        return "Яркость изменена" if ok else str(error)

    if name == "shutdown_computer":
        speak("Вы уверены, что хотите выключить компьютер? Скажите да или нет")
        if "да" in listen().lower():
            speak("Хорошо, компьютер выключается")
            subprocess.run(["shutdown", "/s", "/t", "5"])
            return "Пользователь подтвердил, выключение запущено"
        speak("Отменено")
        return "Пользователь отменил выключение"

    if name == "restart_computer":
        speak("Вы уверены, что хотите перезагрузить компьютер? Скажите да или нет")
        if "да" in listen().lower():
            speak("Хорошо, компьютер перезагружается")
            subprocess.run(["shutdown", "/r", "/t", "5"])
            return "Пользователь подтвердил, перезагрузка запущена"
        speak("Отменено")
        return "Пользователь отменил перезагрузку"

    speak("Не смог выполнить эту команду")
    return "Неизвестное действие"


# ============================================================
#  GUI OYNA — ekran pastida chiqadigan kichik oynacha
# ============================================================

WIDTH = 540
HEIGHT = 92
READY_STATUS = "\U0001F916 Готов. Скажите \"компьютер\" или напишите здесь"

COLOR_IDLE = "#9aa0a6"
COLOR_LISTENING = "#8ab4f8"
COLOR_REPLY = "#e8eaed"
COLOR_ERROR = "#f28b82"

COLOR_MIC_IDLE = "#8ab4f8"
COLOR_MIC_ACTIVE = "#ea4335"


class AssistantWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hey Computer")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.97)
        self.root.configure(bg="#202124")
        self._position_window()
        self._build_ui()
        self._round_corners()

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.speak_lock = threading.Lock()

        self.mic_lock = threading.Lock()
        self.busy = threading.Event()
        self.command_queue = queue.Queue()
        self.root.after(100, self._poll_queue)

        threading.Thread(target=self._wake_word_loop, daemon=True).start()

    # ---------- UI qurish ----------

    def _position_window(self):
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - WIDTH) // 2
        y = screen_h - HEIGHT - 60
        self.root.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")

    def _build_ui(self):
        status_font = tkfont.Font(family="Segoe UI", size=10)
        entry_font = tkfont.Font(family="Segoe UI", size=13)

        accent = tk.Frame(self.root, bg="#8ab4f8", height=3)
        accent.pack(fill="x", side="top")

        top_row = tk.Frame(self.root, bg="#202124")
        top_row.pack(fill="x", padx=16, pady=(10, 0))

        self.status_var = tk.StringVar(value=READY_STATUS)
        self.status_label = tk.Label(
            top_row, textvariable=self.status_var, bg="#202124", fg="#9aa0a6",
            font=status_font, anchor="w",
        )
        self.status_label.pack(side="left", fill="x", expand=True)
        self.status_label.bind("<ButtonPress-1>", self._start_drag)
        self.status_label.bind("<B1-Motion>", self._on_drag)

        close_btn = tk.Button(
            top_row, text="✕", command=self.root.destroy, bg="#202124",
            fg="#9aa0a6", activebackground="#202124", activeforeground="#e8eaed",
            relief="flat", bd=0, font=status_font, cursor="hand2",
        )
        close_btn.pack(side="right")

        row = tk.Frame(self.root, bg="#202124")
        row.pack(fill="x", padx=16, pady=(6, 14))

        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(
            row, textvariable=self.entry_var, font=entry_font, bg="#303134",
            fg="#e8eaed", insertbackground="#e8eaed", relief="flat",
            highlightthickness=1, highlightbackground="#3c4043", highlightcolor="#8ab4f8",
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 10))
        self.entry.bind("<Return>", self._on_submit_text)

        self.mic_button = tk.Button(
            row, text="\U0001F3A4", font=("Segoe UI", 14), bg=COLOR_MIC_IDLE,
            fg="#202124", activebackground=COLOR_MIC_IDLE, relief="flat",
            command=self._on_mic_click, width=3, cursor="hand2",
        )
        self.mic_button.pack(side="right")

    def _round_corners(self):
        # Windows 11'da oyna burchaklarini yumaloqlashtiradi. Windows 10'da
        # bu DWM atributi mavjud emas, shuning uchun xato bo'lsa e'tiborsiz
        # qoldiramiz - oyna oddiy to'rtburchak bo'lib qoladi.
        try:
            hwnd = self.root.winfo_id()
            DWMWA_WINDOW_CORNER_PREFERENCE = 33
            DWMWCP_ROUND = 2
            pref = ctypes.c_int(DWMWCP_ROUND)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_WINDOW_CORNER_PREFERENCE, ctypes.byref(pref), ctypes.sizeof(pref)
            )
        except (AttributeError, OSError):
            pass

    def _start_drag(self, event):
        self._drag_offset = (event.x, event.y)

    def _on_drag(self, event):
        x = self.root.winfo_pointerx() - self._drag_offset[0]
        y = self.root.winfo_pointery() - self._drag_offset[1]
        self.root.geometry(f"+{x}+{y}")

    def speak(self, text):
        # Har safar yangi pyttsx3 dvigatelini yaratamiz. Bitta umumiy
        # dvigatelni turli fon oqimlaridan (background thread) qayta-qayta
        # ishlatish Windows SAPI5'ning COM apartment cheklovi tufayli
        # ba'zan birinchi muvaffaqiyatli chaqiruvdan keyin sukut bo'yicha
        # (xatosiz) osilib qolishiga sabab bo'lgan - shu bilan "faqat bir
        # marta ishlaydi" muammosi kelib chiqqan.
        with self.speak_lock:
            engine = pyttsx3.init()
            configure_voice(engine)
            engine.say(text)
            engine.runAndWait()
            engine.stop()

    # ---------- Asosiy oqim (thread-safe navbat orqali UI yangilanadi) ----------

    def _poll_queue(self):
        try:
            while True:
                item = self.command_queue.get_nowait()
                if item[0] == "status":
                    _, text, color = item
                    self.status_var.set(text)
                    self.status_label.configure(fg=color)
                elif item[0] == "mic_color":
                    _, color = item
                    self.mic_button.configure(bg=color, activebackground=color)
        except queue.Empty:
            pass
        self.root.after(100, self._poll_queue)

    def _set_status(self, text, color=COLOR_IDLE):
        self.command_queue.put(("status", text, color))

    def _set_mic_color(self, color):
        self.command_queue.put(("mic_color", color))

    def _listen(self, timeout=5, phrase_time_limit=6):
        # Mikrofon bir vaqtning o'zida faqat bitta joydan (uyg'otuvchi so'z
        # tsikli, mikrofon tugmasi yoki matn orqali tasdiqlash) ishlatilishi
        # kerak, aks holda SpeechRecognition xato beradi. Shu sababli
        # navbatga qo'yamiz.
        with self.mic_lock:
            with self.microphone as source:
                try:
                    audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                except sr.WaitTimeoutError:
                    return ""
        try:
            return self.recognizer.recognize_google(audio, language=LANGUAGE)
        except (sr.UnknownValueError, sr.RequestError):
            return ""

    def _dispatch_and_report(self, text):
        self._set_status(f"Вы: {text}", COLOR_REPLY)

        def speak_and_show(reply):
            self._set_status(reply, COLOR_REPLY)
            self.speak(reply)

        def confirm_listen():
            return self._listen(timeout=5, phrase_time_limit=4)

        try:
            if ai_is_configured():
                ai_handle(text, speak_and_show, confirm_listen)
            else:
                dispatch(text, speak_and_show, confirm_listen)
        except Exception as exc:  # noqa: BLE001 - buyruq turlari xilma-xil, biror xato butun yordamchini o'chirib qo'ymasligi kerak
            self._set_status(f"Ошибка: {exc}", COLOR_ERROR)
        threading.Timer(4.0, lambda: self._set_status(READY_STATUS)).start()

    # ---------- Matn orqali buyruq ----------

    def _on_submit_text(self, _event=None):
        text = self.entry_var.get().strip()
        if not text or self.busy.is_set():
            return
        self.entry_var.set("")
        threading.Thread(target=self._run_busy, args=(text,), daemon=True).start()

    def _run_busy(self, text):
        self.busy.set()
        try:
            self._dispatch_and_report(text)
        finally:
            self.busy.clear()

    # ---------- Mikrofon tugmasi orqali buyruq ----------

    def _on_mic_click(self):
        if self.busy.is_set():
            return
        threading.Thread(target=self._voice_command_flow, daemon=True).start()

    def _voice_command_flow(self):
        self.busy.set()
        self._set_mic_color(COLOR_MIC_ACTIVE)
        try:
            self._set_status("Слушаю...", COLOR_LISTENING)
            text = self._listen(timeout=5, phrase_time_limit=6)
            if text:
                self._dispatch_and_report(text)
            else:
                self._set_status("Не расслышал, повторите", COLOR_ERROR)
                threading.Timer(2.5, lambda: self._set_status(READY_STATUS)).start()
        finally:
            self.busy.clear()
            self._set_mic_color(COLOR_MIC_IDLE)

    # ---------- Fonda uyg'otuvchi so'zni kutish ----------

    def _wake_word_loop(self):
        with self.mic_lock:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
        while True:
            if self.busy.is_set():
                time.sleep(0.2)
                continue
            heard = self._listen(timeout=4, phrase_time_limit=4)
            if not heard or not wake_word_detected(heard.lower(), WAKE_WORDS):
                continue

            self.busy.set()
            self._set_mic_color(COLOR_MIC_ACTIVE)
            try:
                self._set_status("Слушаю...", COLOR_LISTENING)
                command_text = self._listen(timeout=5, phrase_time_limit=6)
                if command_text:
                    self._dispatch_and_report(command_text)
                else:
                    self._set_status(READY_STATUS)
            finally:
                self.busy.clear()
                self._set_mic_color(COLOR_MIC_IDLE)

    def run(self):
        self.root.mainloop()


# ============================================================
#  AVTOMATIK ISHGA TUSHIRISH (Windows Startup papkasi)
# ============================================================

def _startup_vbs_path():
    startup_dir = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    return startup_dir, startup_dir / "hey_computer_assistant.vbs"


def _pythonw_path():
    pythonw = Path(sys.executable).with_name("pythonw.exe")
    if pythonw.exists():
        return pythonw
    return Path(sys.executable)


def install_autostart():
    project_dir = Path(__file__).resolve().parent
    script_path = Path(__file__).resolve()
    startup_dir, vbs_path = _startup_vbs_path()
    pythonw = _pythonw_path()

    vbs_content = (
        'Set objShell = CreateObject("WScript.Shell")\n'
        f'objShell.CurrentDirectory = "{project_dir}"\n'
        f'objShell.Run """{pythonw}"" ""{script_path}""", 0, False\n'
    )
    startup_dir.mkdir(parents=True, exist_ok=True)
    vbs_path.write_text(vbs_content, encoding="utf-8")

    print("Готово! Ассистент теперь будет запускаться автоматически при")
    print("включении/входе в Windows - без терминала и без окна консоли.")
    print(f"\nФайл автозапуска: {vbs_path}")
    print("Чтобы отключить: python hey_computer.py --uninstall-autostart")


def uninstall_autostart():
    _, vbs_path = _startup_vbs_path()
    if vbs_path.exists():
        vbs_path.unlink()
        print("Автозапуск отключён.")
    else:
        print("Автозапуск не найден - возможно, уже был отключён.")


# ============================================================
#  ASOSIY
# ============================================================

if __name__ == "__main__":
    if "--install-autostart" in sys.argv:
        install_autostart()
    elif "--uninstall-autostart" in sys.argv:
        uninstall_autostart()
    else:
        AssistantWindow().run()
