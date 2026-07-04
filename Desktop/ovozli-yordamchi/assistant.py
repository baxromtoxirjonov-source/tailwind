"""Doim fonda tinglab turadigan, uyg'otuvchi so'zga javob beradigan ovozli
yordamchi.

Ishga tushirish:
    python assistant.py

Uyg'otuvchi so'zlardan birini ayting (config.py dagi WAKE_WORDS), so'ng
signaldan keyin buyruqni ayting.
"""

import speech_recognition as sr
import pyttsx3

import config
from commands import dispatch

recognizer = sr.Recognizer()
microphone = sr.Microphone()
tts_engine = pyttsx3.init()


def speak(text):
    print(f"Yordamchi: {text}")
    tts_engine.say(text)
    tts_engine.runAndWait()


def listen(timeout=5, phrase_time_limit=6):
    with microphone as source:
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            return ""

    try:
        text = recognizer.recognize_google(audio, language=config.LANGUAGE)
        print(f"Eshitildi: {text}")
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as exc:
        print(f"Tanish xizmatiga ulanib bo'lmadi: {exc}")
        return ""


def main():
    with microphone as source:
        print("Atrofdagi shovqinga moslashtirilmoqda...")
        recognizer.adjust_for_ambient_noise(source, duration=1)

    print("Tayyor. Uyg'otuvchi so'zni kuting:", ", ".join(config.WAKE_WORDS))
    while True:
        heard = listen(timeout=None, phrase_time_limit=4)
        if not heard:
            continue

        lowered = heard.lower()
        if any(wake_word in lowered for wake_word in config.WAKE_WORDS):
            speak("Eshityapman")
            command_text = listen(timeout=5, phrase_time_limit=6)
            dispatch(command_text, speak, lambda: listen(timeout=5, phrase_time_limit=4))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nYordamchi to'xtatildi")
