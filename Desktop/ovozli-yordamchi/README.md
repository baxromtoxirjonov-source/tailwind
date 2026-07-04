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
- Uzoq umr ko'rish uchun avtomatik ishga tushirishni xohlasangiz, bu skriptni
  Windows Task Scheduler yoki Startup papkasiga qo'shishingiz mumkin.
- "Kompyuterni o'chir" / "qayta yoqish" buyruqlari xato eshitilib ketmasligi
  uchun har doim "Ha/Yo'q" deb tasdiqlashni so'raydi.
