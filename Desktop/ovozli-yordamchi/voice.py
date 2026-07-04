"""TTS ovozini tanlash: avval nutqni tanish tiliga (config.LANGUAGE) mos
ovoz, topilmasa ayol ovozi, u ham bo'lmasa standart ovoz."""

import config

LANG_NAME_HINTS = {
    "ru": ("russian",),
    "uz": ("uzbek",),
    "en": ("english",),
}

FEMALE_HINTS = ("zira", "female", "ayol", "hazel", "susan", "eva")


def configure_voice(tts_engine):
    voices = tts_engine.getProperty("voices")
    lang_prefix = config.LANGUAGE.split("-")[0].lower()
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
