# Yordamchi sozlamalari. Bu faylni tahrirlab, o'zingizga moslashtiring.

# Uyg'otuvchi so'z (shu so'zlardan birini aytsangiz, yordamchi buyruqni
# kuta boshlaydi)
WAKE_WORDS = ["компьютер", "эй компьютер", "хей компьютер", "привет компьютер"]

# Nutqni tanish tili. Ruscha gapirish uchun "ru-RU" qo'yilgan.
#
# MUHIM: commands.py dagi kalit so'zli (qat'iy) buyruq tanish tizimi
# lotin-o'zbekcha yozilgan ("och", "qidir", "papka"...) va shuning uchun
# ru-RU tanish natijasi bilan mos kelmaydi. Bu muammo emas, chunki AI
# yoqilgan bo'lsa (ANTHROPIC_API_KEY o'rnatilgan bo'lsa) barcha buyruqlar
# ai_router.py orqali - matnning qaysi tilda bo'lishidan qat'iy nazar -
# tushuniladi. commands.py faqat AI o'rnatilmagan hollarda zaxira sifatida
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

# --- AI orqali tushunish (ixtiyoriy, ai_router.py) ---
# Buyruqni qat'iy kalit so'zlar o'rniga Claude AI yordamida tushunish uchun
# ANTHROPIC_API_KEY muhit o'zgaruvchisini o'rnatish kerak (console.anthropic.com
# dan olinadi). Bu pullik - har bir buyruq uchun kichik summa yechiladi.
#
# Standart model eng qobiliyatli model (claude-opus-4-8). Bu ovozli buyruqlarni
# tez-tez, kichik va sodda so'rovlar bilan aniqlaydigan vazifa bo'lgani uchun,
# tezlik/narx muhimroq bo'lsa, quyidagini "claude-haiku-4-5" ga almashtirishingiz
# mumkin - sifat farqi bu oddiy buyruqlar uchun deyarli sezilmaydi.
AI_MODEL = "claude-opus-4-8"
