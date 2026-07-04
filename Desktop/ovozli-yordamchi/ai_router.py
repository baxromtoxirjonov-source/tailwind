"""Claude AI (Anthropic Messages API, tool use) orqali erkin gapni tushunib,
mos amalni bajaradigan va suhbat tarixini eslab qoladigan modul. Ishlashi
uchun ANTHROPIC_API_KEY muhit o'zgaruvchisi o'rnatilgan bo'lishi kerak.

Javoblar ruscha beriladi (config.LANGUAGE = "ru-RU" bilan mos). API kalit
o'rnatilmagan bo'lsa, commands.dispatch() (o'zbekcha, kalit-so'zli) zaxira
sifatida ishlatiladi.
"""

import datetime
import os
import subprocess

import anthropic

import commands
import config

TOOLS = [
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

SYSTEM_PROMPT = (
    "Ты — голосовой ассистент на личном компьютере пользователя. "
    "Отвечай всегда на русском языке, кратко и по-разговорному, без длинных "
    "списков и заголовков. Если сказанное подходит под одно из доступных "
    "действий (tools) — вызови его. Если это обычный разговор, приветствие "
    "или вопрос, на который не нужно действие компьютера — просто ответь "
    "текстом, как в обычной беседе."
)

MAX_HISTORY_MESSAGES = 20

_history = []


def is_configured():
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def handle(text, speak, listen):
    """Matnni Claude'ga suhbat tarixi bilan yuboradi: tanlagan vositasini
    bajaradi yoki oddiy matn javobini o'qib beradi. Suhbat tarixi keyingi
    chaqiruvlar uchun saqlanadi."""
    client = anthropic.Anthropic()
    _history.append({"role": "user", "content": text})

    response = client.messages.create(
        model=config.AI_MODEL,
        max_tokens=300,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=_history,
    )

    tool_use = next((block for block in response.content if block.type == "tool_use"), None)
    if tool_use is None:
        reply = "".join(block.text for block in response.content if block.type == "text").strip()
        reply = reply or "Не понял, повторите, пожалуйста"
        _history.append({"role": "assistant", "content": reply})
        speak(reply)
        _trim_history()
        return

    _history.append({"role": "assistant", "content": response.content})
    result_summary = _run_tool(tool_use.name, tool_use.input or {}, speak, listen)
    _history.append(
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
    _trim_history()


def _trim_history():
    # Uzoq suhbatda xabarlar cheksiz ko'payib ketmasligi uchun oxirgi
    # N ta xabarni saqlaymiz.
    if len(_history) > MAX_HISTORY_MESSAGES:
        del _history[: len(_history) - MAX_HISTORY_MESSAGES]


def _match(name, mapping):
    name = (name or "").lower()
    for key in mapping:
        if key in name or name in key:
            return key
    return None


def _run_tool(name, args, speak, listen):
    """Vositani bajaradi, ovoz bilan javob beradi va Claude uchun qisqa
    natija matnini qaytaradi (suhbat tarixiga yozish uchun)."""

    if name == "open_app":
        match = _match(args.get("name"), config.APPS)
        if match and commands.open_app(config.APPS[match]):
            speak(f"Открываю {match}")
            return f"Открыл {match}"
        speak(f"Не нашёл программу {args.get('name')}")
        return "Программа не найдена"

    if name == "open_site":
        raw_name = (args.get("name") or "").strip()
        match = _match(raw_name, config.SITES)
        if match:
            commands.webbrowser.open(config.SITES[match])
            speak(f"Открываю {match}")
            return f"Открыл сайт {match}"
        guess = raw_name.lower().replace(" ", "")
        commands.webbrowser.open(f"https://{guess}.com")
        speak(f"Пытаюсь открыть сайт {guess}")
        return f"Попытался открыть {guess}.com"

    if name == "open_folder":
        match = _match(args.get("name"), config.FOLDERS)
        if match:
            os.startfile(commands.HOME / config.FOLDERS[match])
            speak(f"Открыл папку {match}")
            return f"Открыл папку {match}"
        speak(f"Не нашёл папку {args.get('name')}")
        return "Папка не найдена"

    if name == "find_file":
        found = commands.find_file(args.get("name", ""))
        if found:
            os.startfile(found)
            speak(f"Нашёл {args.get('name')} и открыл")
            return f"Файл найден и открыт: {found}"
        speak(f"Файл {args.get('name')} не найден")
        return "Файл не найден"

    if name == "create_folder":
        folder_name = args.get("name") or "Новая папка"
        new_path = commands.HOME / "Desktop" / folder_name
        new_path.mkdir(parents=True, exist_ok=True)
        speak(f"Папка {folder_name} создана на рабочем столе")
        return f"Папка {folder_name} создана"

    if name == "web_search":
        query = args.get("query", "")
        commands.webbrowser.open(f"https://www.google.com/search?q={query}")
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
        ok, error = commands.change_volume(delta)
        speak("Готово" if ok else error)
        return "Громкость изменена" if ok else str(error)

    if name == "brightness_control":
        delta = {"up": 15, "down": -15}.get(args.get("direction"), 0)
        ok, error = commands.change_brightness(delta)
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
