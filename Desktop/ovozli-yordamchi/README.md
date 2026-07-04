# Ovozli yordamchi (Windows)

Doim fonda tinglab turadigan, "kompyuter" (yoki config.py dagi boshqa
uyg'otuvchi so'z) aytilganda buyruqni kutadigan va bajaradigan ovozli
yordamchi.

## O'rnatish

```
pip install -r requirements.txt
```

Agar `PyAudio` o'rnatilmasa, quyidagicha urinib ko'ring:

```
pip install pipwin
pipwin install pyaudio
```

## Ishga tushirish

**Oynali versiya (tavsiya etiladi)** — Google Assistant kabi ekran pastida
kichik oynacha chiqadi, unga yozib ham, mikrofon tugmasini bosib gapirib ham,
"kompyuter" deb uyg'otib ham buyruq berish mumkin:

```
python gui_assistant.py
```

**Konsol versiyasi** — faqat ovoz orqali, oynasiz ishlaydi:

```
python assistant.py
```

Terminal "Tayyor..." deb yozgach, uyg'otuvchi so'zlardan birini ayting
(masalan "kompyuter"). Yordamchi "Eshityapman" deb javob bergach, buyruqni
ayting.

## Namuna buyruqlar

- "Chrome ochib ber" / "YouTube ochib ber" / "Notepad ochib ber"
- "Desktop papkasini och" / "Downloads papkasini och"
- "Hisobot nomli faylni qidir"
- "Ish nomli papka yarat"
- "Google'dan tashkent ob havosi qidir"
- "Soat nechi" / "Bugun nechi sana"
- "Ovozni baland qil" / "Ovozni past qil"
- "Yorqinlikni oshir" / "Yorqinlikni kamaytir"
- "Kompyuterni o'chir" (keyin "Ha" deb tasdiqlash so'raladi)

## Sozlash

`config.py` faylida quyidagilarni o'zgartirish mumkin:

- `WAKE_WORDS` — uyg'otuvchi so'zlar ro'yxati
- `LANGUAGE` — nutqni tanish tili (`uz-UZ`, agar aniq tanimasa `ru-RU` yoki
  `en-US` ga almashtiring)
- `APPS`, `SITES`, `FOLDERS` — ovoz bilan ochsa bo'ladigan dastur/sayt/papka
  nomlari

## Bilish kerak bo'lgan cheklovlar

- Nutqni tanish Google'ning bepul onlayn xizmati orqali ishlaydi — internet
  aloqasi kerak.
- Javob matni har doim o'zbekcha bo'ladi. Ovoz chiqarib gapirish (TTS) esa
  Windows'da o'rnatilgan tizim ovozlari orqali ishlaydi — aksariyat
  Windows'larda o'zbekcha ovoz o'rnatilmagan bo'ladi, shuning uchun matn
  o'zbekcha bo'lsa-da, talaffuz boshqa til (masalan ingliz yoki rus)
  aksentida eshitilishi mumkin. Agar bu yoqmasa, `gui_assistant.py` dagi
  `self.speak(...)` chaqiruvlarini olib tashlab, faqat matn ko'rinishini
  qoldirish mumkin.
- Uzoq umr ko'rish uchun avtomatik ishga tushirishni xohlasangiz, bu skriptni
  Windows Task Scheduler yoki Startup papkasiga qo'shishingiz mumkin.
- "Kompyuterni o'chir" / "qayta yoqish" buyruqlari xato eshitilib ketmasligi
  uchun har doim "Ha/Yo'q" deb tasdiqlashni so'raydi.

## Agar hech narsa ishlamasa (mikrofon hech narsani tanimasa)

Bularni tekshiring:

1. **PyAudio o'rnatilganmi?** `python -c "import pyaudio"` xatosiz ishlasa,
   demak o'rnatilgan. Xato chiqsa, "O'rnatish" bo'limidagi `pipwin` usulini
   sinab ko'ring.
2. **Windows mikrofon ruxsati.** Sozlamalar → Maxfiylik va xavfsizlik →
   Mikrofon → "Ilovalarga mikrofondan foydalanishga ruxsat berish" yoqilganligini
   tekshiring.
3. **Tanish tili.** `config.py` dagi `LANGUAGE = "uz-UZ"` ba'zi mikrofon/aksent
   uchun yaxshi ishlamasligi mumkin. `"ru-RU"` yoki `"en-US"` ga almashtirib,
   o'sha tilda gapirib ko'ring — muammo tilga bog'liqmi yoki mikrofonga
   bog'liqmi shu orqali bilib olasiz.
4. **Terminaldagi xabarlarni o'qing** (`assistant.py` ishlatayotgan bo'lsangiz)
   — "Eshitildi: ..." qatori chiqmasa, ovoz umuman mikrofonga yetib
   bormayapti degani (mikrofon tanlash yoki ruxsat muammosi).
