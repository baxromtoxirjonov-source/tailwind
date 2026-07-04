"""TTS ovozini tanlash: avval o'zbekcha ovoz, topilmasa ayol ovozi."""

FEMALE_HINTS = ("zira", "female", "ayol", "hazel", "susan", "eva")


def configure_voice(tts_engine):
    voices = tts_engine.getProperty("voices")

    for voice in voices:
        name = (voice.name or "").lower()
        langs = [str(lang).lower() for lang in getattr(voice, "languages", [])]
        if "uz" in name or any("uz" in lang for lang in langs):
            tts_engine.setProperty("voice", voice.id)
            return

    for voice in voices:
        name = (voice.name or "").lower()
        gender = str(getattr(voice, "gender", "") or "").lower()
        if "female" in gender or any(hint in name for hint in FEMALE_HINTS):
            tts_engine.setProperty("voice", voice.id)
            return

    # Hech qanday moslik topilmasa, standart ovoz qoladi - matn baribir
    # o'zbekcha bo'ladi, faqat talaffuz aksenti boshqacha bo'lishi mumkin.
