# Yordamchi sozlamalari. Bu faylni tahrirlab, o'zingizga moslashtiring.

# Uyg'otuvchi so'z (shu so'zni aytsangiz, yordamchi buyruqni kuta boshlaydi)
WAKE_WORDS = ["kompyuter"]

# Nutqni tanish tili. MUHIM: commands.py dagi barcha buyruq so'zlari
# (och, qidir, papka, ovoz...) lotin-o'zbekcha yozilgan. Agar bu yerni
# "ru-RU" yoki boshqa tilga o'zgartirsangiz, tanish natijasi boshqa
# alifbo/tilda qaytadi va hech qanday buyruq mos kelmay qoladi - shuning
# uchun tilni o'zgartirsangiz, commands.py dagi kalit so'zlarni ham o'sha
# tilga tarjima qilish kerak bo'ladi.
LANGUAGE = "uz-UZ"

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
