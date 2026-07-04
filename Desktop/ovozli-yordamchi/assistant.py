"""Doim fonda tinglab turadigan, uyg'otuvchi so'zga javob beradigan ovozli
yordamchi.

Ishga tushirish:
    python assistant.py

Uyg'otuvchi so'zlardan birini ayting (config.py dagi WAKE_WORDS), so'ng
signaldan keyin buyruqni ayting.
"""

import speech_recognition as sr
import pyttsx3

import ai_router
import config
from commands import dispatch
from voice import configure_voice
from wakeword import wake_word_detected

recognizer = sr.Recognizer()
microphone = sr.Microphone()
tts_engine = pyttsx3.init()
configure_voice(tts_engine)


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
        print(f"Услышано: {text}")
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as exc:
        print(f"Не удалось подключиться к сервису распознавания: {exc}")
        return ""


def main():
    with microphone as source:
        print("Настройка под окружающий шум...")
        recognizer.adjust_for_ambient_noise(source, duration=1)

    print("Готов. Ожидаю слово пробуждения:", ", ".join(config.WAKE_WORDS))
    while True:
        heard = listen(timeout=None, phrase_time_limit=4)
        if not heard:
            continue

        lowered = heard.lower()
        if wake_word_detected(lowered, config.WAKE_WORDS):
            speak("Слушаю")
            command_text = listen(timeout=5, phrase_time_limit=6)
            confirm_listen = lambda: listen(timeout=5, phrase_time_limit=4)
            try:
                if ai_router.is_configured():
                    ai_router.handle(command_text, speak, confirm_listen)
                else:
                    dispatch(command_text, speak, confirm_listen)
            except Exception as exc:  # noqa: BLE001 - bitta buyruq xatosi yordamchini o'chirib qo'ymasligi kerak
                speak(f"Произошла ошибка: {exc}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nАссистент остановлен")
