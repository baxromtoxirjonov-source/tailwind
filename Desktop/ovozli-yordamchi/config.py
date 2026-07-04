# Yordamchi sozlamalari. Bu faylni tahrirlab, o'zingizga moslashtiring.

# Uyg'otuvchi so'zlar (shulardan birini aytsangiz, yordamchi buyruqni kuta boshlaydi)
WAKE_WORDS = ["kompyuter", "hey kompyuter", "ey kompyuter", "ok kompyuter"]

# Nutqni tanish tili. Agar tanish sifatsiz bo'lsa "ru-RU" yoki "en-US" ga
# almashtirib ko'ring - Google'ning bepul tanish xizmati ba'zi tillarda
# boshqalariga qaraganda aniqroq ishlaydi.
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
