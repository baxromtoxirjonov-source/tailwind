# Hey Computer — ovozli AI yordamchi (Windows)

Doim fonda tinglab turadigan, "компьютер" (yoki config.py dagi boshqa
uyg'otuvchi so'z) aytilganda buyruqni kutadigan va bajaradigan ovozli
yordamchi. Nutqni tanish va javoblar ruscha ishlaydi (`config.LANGUAGE`).

## O'rnatish

**0-qadam — Python o'rnatilganligini tekshiring.** Terminalga `python
--version` yozing. Agar versiya raqami chiqmasa (masalan Microsoft Store
ochilib ketsa yoki hech narsa chiqmasa), demak Python haqiqiy
o'rnatilmagan — faqat Windows'ning "o'rnat" tugmasi bor. Quyidagi qadamlar
shu tufayli "hech narsa ishlamayapti" bo'lib ko'rinadi:

1. https://www.python.org/downloads/ dan Python'ni yuklab oling
2. O'rnatishda **"Add python.exe to PATH"** katagini albatta belgilang
3. Terminalni yopib qayta oching, `python --version` bilan tekshiring

Shundan keyingina quyidagini bajaring:

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

Terminal "Готов..." deb yozgach, uyg'otuvchi so'zlardan birini ayting
(masalan "компьютер"). Yordamchi "Слушаю" deb javob bergach, buyruqni
ayting.

## Avtomatik ishga tushirish (Windows yonganda o'zi ishga tushishi)

Har safar terminal ochib `python gui_assistant.py` yozishning hojati
bo'lmasin desangiz, bir marta shuni ishga tushiring:

```
python install_autostart.py
```

Shundan keyin yordamchi Windows yoqilganda/kirganda avtomatik, terminalsiz
ishga tushadi — sizga faqat "компьютер" deb aytish qoladi. O'chirish uchun:
`python uninstall_autostart.py`.

## Namuna buyruqlar

AI yoqilgan bo'lsa (pastdagi bo'limga qarang), erkin gapirish yetarli —
masalan "открой хром", "включи ютуб", "какая сейчас погода", "сколько
время" kabi. AI yoqilmagan bo'lsa (zaxira rejim), qat'iy o'zbekcha kalit
so'zlar ishlatiladi:

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

- `WAKE_WORDS` — uyg'otuvchi so'zlar ro'yxati (hozir ruscha)
- `LANGUAGE` — nutqni tanish tili (hozir `ru-RU`)
- `APPS`, `SITES`, `FOLDERS` — ovoz bilan ochsa bo'ladigan dastur/sayt/papka
  nomlari (bular zaxira/kalit-so'z rejimi uchun; AI yoqilgan bo'lsa ham
  ulardan foydalaniladi, lekin AI istalgan boshqa nomni ham tushunadi)

## Bilish kerak bo'lgan cheklovlar

- Nutqni tanish Google'ning bepul onlayn xizmati orqali ishlaydi — internet
  aloqasi kerak.
- Javob matni AI yoqilgan bo'lsa ruscha bo'ladi (`ai_router.py`), AI
  yoqilmagan zaxira rejimida esa o'zbekcha bo'ladi (`commands.py`). Ovoz
  chiqarib gapirish (TTS) Windows'da o'rnatilgan tizim ovozlari orqali
  ishlaydi (`voice.py`): avval nutq tiliga mos ovoz (ruscha) qidiriladi,
  topilmasa ayol ovozi (masalan "Zira") tanlanadi, u ham bo'lmasa standart
  ovoz qoladi. Agar kompyuteringizda ruscha ovoz o'rnatilmagan bo'lsa,
  matn to'g'ri bo'lsa-da, talaffuz boshqa til aksentida eshitilishi mumkin.
- "Kompyuterni o'chir" / "qayta yoqish" buyruqlari xato eshitilib ketmasligi
  uchun har doim "Да/Нет" deb tasdiqlashni so'raydi.

## AI orqali "aqlli" tushunish va ruscha suhbat (ixtiyoriy, lekin tavsiya etiladi)

Standart holatda (API kalitisiz) yordamchi qat'iy o'zbekcha kalit so'zlar
("och", "qidir", "papka"...) orqali ishlaydi. Claude AI'ni ulasangiz, erkin
ruscha gapirish, savol-javob va suhbat tarixini eslab qolish ham ishlaydi:

1. https://console.anthropic.com dan hisob oching va API kalit yarating
2. Kalitni muhit o'zgaruvchisi sifatida o'rnating:
   - PowerShell: `setx ANTHROPIC_API_KEY "sk-ant-..."`  (keyin terminalni qayta oching)
3. `pip install -r requirements.txt` (endi `anthropic` kutubxonasini ham o'rnatadi)

Kalit o'rnatilgan bo'lsa, yordamchi avtomatik ravishda AI orqali tushunishga
o'tadi (`ai_router.py`) — endi faqat buyruq emas, oddiy savollarga ham ruscha
javob beradi va oldingi gaplaringizni suhbat davomida eslab qoladi. Kalit
o'rnatilmagan bo'lsa, avvalgidek oddiy kalit-so'z rejimida ishlayveradi.

**Narxi haqida:** bu pullik xizmat — har bir ovozli buyruq/savol uchun juda
kichik summa (bir necha sentning ulushi) yechiladi. Standart model eng
qobiliyatlisi (`claude-opus-4-8`); tezlik/narx muhimroq bo'lsa `config.py`
dagi `AI_MODEL` ni `"claude-haiku-4-5"` ga almashtiring — bu oddiy
buyruqlar uchun deyarli bir xil ishlaydi, lekin ancha arzon va tezroq.

## Agar hech narsa ishlamasa (mikrofon hech narsani tanimasa)

Bularni tekshiring:

1. **PyAudio o'rnatilganmi?** `python -c "import pyaudio"` xatosiz ishlasa,
   demak o'rnatilgan. Xato chiqsa, "O'rnatish" bo'limidagi `pipwin` usulini
   sinab ko'ring.
2. **Windows mikrofon ruxsati.** Sozlamalar → Maxfiylik va xavfsizlik →
   Mikrofon → "Ilovalarga mikrofondan foydalanishga ruxsat berish" yoqilganligini
   tekshiring.
3. **Tanish tili.** `config.py` dagi `LANGUAGE = "ru-RU"` ba'zi mikrofon/aksent
   uchun yaxshi ishlamasligi mumkin. `"uz-UZ"` yoki `"en-US"` ga almashtirib,
   o'sha tilda gapirib ko'ring — muammo tilga bog'liqmi yoki mikrofonga
   bog'liqmi shu orqali bilib olasiz. **Eslatma:** tilni o'zgartirsangiz,
   AI o'rnatilmagan hollarda ishlaydigan zaxira `commands.py` o'zbekcha
   kalit so'zlar bilan ishlaydi — shuning uchun eng ishonchli yechim doim
   AI'ni yoqib qo'yish (yuqoridagi bo'limga qarang).
4. **Terminaldagi xabarlarni o'qing** (`assistant.py` ishlatayotgan bo'lsangiz)
   — "Услышано: ..." qatori chiqmasa, ovoz umuman mikrofonga yetib
   bormayapti degani (mikrofon tanlash yoki ruxsat muammosi).
