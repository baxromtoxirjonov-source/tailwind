"""Claude AI (Anthropic Messages API, tool use) orqali erkin gapni tushunib,
mos amalni bajaradigan modul. Ishlashi uchun ANTHROPIC_API_KEY muhit
o'zgaruvchisi o'rnatilgan bo'lishi kerak.

Buyruq har doim kalit-so'z asosidagi commands.dispatch() bilan ham ishlaydi -
bu modul shunga qo'shimcha, "aqlliroq" tushunish uchun ixtiyoriy variant.
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
        "description": "Kompyuterda o'rnatilgan dasturni ochish (masalan Chrome, Notepad, Kalkulyator, Word, Excel).",
        "input_schema": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "Dastur nomi"}},
            "required": ["name"],
        },
    },
    {
        "name": "open_site",
        "description": "Veb-saytni brauzerda ochish (masalan YouTube, Google, Instagram, Gmail, yoki boshqa istalgan sayt nomi).",
        "input_schema": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "Sayt nomi"}},
            "required": ["name"],
        },
    },
    {
        "name": "open_folder",
        "description": "Kompyuterdagi papkani ochish (Desktop, Downloads, Documents).",
        "input_schema": {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        },
    },
    {
        "name": "find_file",
        "description": "Kompyuterdan fayl qidirish va topilsa ochish.",
        "input_schema": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "Fayl nomi yoki uning bir qismi"}},
            "required": ["name"],
        },
    },
    {
        "name": "create_folder",
        "description": "Desktop ichida yangi papka yaratish.",
        "input_schema": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "Yaratiladigan papka nomi"}},
            "required": ["name"],
        },
    },
    {
        "name": "web_search",
        "description": "Google'da biror narsani qidirish.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "get_time",
        "description": "Hozirgi vaqtni aytish.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_date",
        "description": "Bugungi sanani aytish.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "volume_control",
        "description": "Ovoz balandligini oshirish, pasaytirish yoki o'chirish.",
        "input_schema": {
            "type": "object",
            "properties": {"direction": {"type": "string", "enum": ["up", "down", "mute"]}},
            "required": ["direction"],
        },
    },
    {
        "name": "brightness_control",
        "description": "Ekran yorqinligini oshirish yoki kamaytirish.",
        "input_schema": {
            "type": "object",
            "properties": {"direction": {"type": "string", "enum": ["up", "down"]}},
            "required": ["direction"],
        },
    },
    {
        "name": "shutdown_computer",
        "description": "Kompyuterni o'chirish. Har doim foydalanuvchidan alohida tasdiq so'raladi.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "restart_computer",
        "description": "Kompyuterni qayta yoqish. Har doim foydalanuvchidan alohida tasdiq so'raladi.",
        "input_schema": {"type": "object", "properties": {}},
    },
]

SYSTEM_PROMPT = (
    "Siz foydalanuvchining shaxsiy kompyuteridagi ovozli yordamchisiz. "
    "Foydalanuvchi aytgan gapga eng mos keladigan vositani (tool) tanlang. "
    "Agar hech qanday amal mos kelmasa - masalan u shunchaki gaplashmoqchi, "
    "salomlashyapti yoki umumiy savol bermoqchi bo'lsa - hech qanday vosita "
    "chaqirmang, o'zingiz oddiy matn bilan qisqa javob bering. Javobingiz "
    "har doim o'zbek tilida bo'lsin."
)


def is_configured():
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def handle(text, speak, listen):
    """Matnni Claude'ga yuborib, tanlagan vositasini bajaradi yoki oddiy
    matn javobini o'qib beradi."""
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=config.AI_MODEL,
        max_tokens=300,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=[{"role": "user", "content": text}],
    )

    tool_use = next((block for block in response.content if block.type == "tool_use"), None)
    if tool_use is None:
        reply = "".join(block.text for block in response.content if block.type == "text").strip()
        speak(reply or "Tushunolmadim")
        return

    _run_tool(tool_use.name, tool_use.input or {}, speak, listen)


def _match(name, mapping):
    name = (name or "").lower()
    for key in mapping:
        if key in name or name in key:
            return key
    return None


def _run_tool(name, args, speak, listen):
    if name == "open_app":
        match = _match(args.get("name"), config.APPS)
        if match and commands.open_app(config.APPS[match]):
            speak(f"{match} ochildi")
        else:
            speak(f"{args.get('name')} nomli dasturni topolmadim")
        return

    if name == "open_site":
        raw_name = (args.get("name") or "").strip()
        match = _match(raw_name, config.SITES)
        if match:
            commands.webbrowser.open(config.SITES[match])
            speak(f"{match} ochildi")
        else:
            guess = raw_name.lower().replace(" ", "")
            commands.webbrowser.open(f"https://{guess}.com")
            speak(f"{guess} saytini ochishga harakat qildim")
        return

    if name == "open_folder":
        match = _match(args.get("name"), config.FOLDERS)
        if match:
            os.startfile(commands.HOME / config.FOLDERS[match])
            speak(f"{match} papkasi ochildi")
        else:
            speak(f"{args.get('name')} nomli papkani topolmadim")
        return

    if name == "find_file":
        found = commands.find_file(args.get("name", ""))
        if found:
            os.startfile(found)
            speak(f"{args.get('name')} topildi va ochildi")
        else:
            speak(f"{args.get('name')} nomli fayl topilmadi")
        return

    if name == "create_folder":
        folder_name = args.get("name") or "Yangi papka"
        new_path = commands.HOME / "Desktop" / folder_name
        new_path.mkdir(parents=True, exist_ok=True)
        speak(f"{folder_name} papkasi Desktop ichida yaratildi")
        return

    if name == "web_search":
        query = args.get("query", "")
        commands.webbrowser.open(f"https://www.google.com/search?q={query}")
        speak(f"{query} uchun qidiruv natijalarini ochdim")
        return

    if name == "get_time":
        speak(f"Hozir soat {datetime.datetime.now().strftime('%H:%M')}")
        return

    if name == "get_date":
        speak(f"Bugun {datetime.datetime.now().strftime('%d.%m.%Y')}")
        return

    if name == "volume_control":
        delta = {"up": 15, "down": -15, "mute": -100}.get(args.get("direction"), 0)
        ok, error = commands.change_volume(delta)
        speak("Bajarildi" if ok else error)
        return

    if name == "brightness_control":
        delta = {"up": 15, "down": -15}.get(args.get("direction"), 0)
        ok, error = commands.change_brightness(delta)
        speak("Bajarildi" if ok else error)
        return

    if name == "shutdown_computer":
        speak("Kompyuterni o'chirishni tasdiqlaysizmi? Ha yoki yo'q deb ayting")
        if "ha" in listen().lower():
            speak("Xayr, kompyuter o'chmoqda")
            subprocess.run(["shutdown", "/s", "/t", "5"])
        else:
            speak("Bekor qilindi")
        return

    if name == "restart_computer":
        speak("Kompyuterni qayta yoqishni tasdiqlaysizmi? Ha yoki yo'q deb ayting")
        if "ha" in listen().lower():
            speak("Kompyuter qayta yoqilmoqda")
            subprocess.run(["shutdown", "/r", "/t", "5"])
        else:
            speak("Bekor qilindi")
        return

    speak("Bu buyruqni bajara olmadim")
