"""Uyg'otuvchi so'zni aniqlash - tasodifiy shovqin ichida uchraydigan
qism-so'zlarni chalg'ib ketmasligi uchun butun so'z sifatida tekshiradi."""


def wake_word_detected(heard_lower, wake_words):
    tokens = heard_lower.split()
    for phrase in wake_words:
        phrase_tokens = phrase.split()
        n = len(phrase_tokens)
        for i in range(len(tokens) - n + 1):
            if tokens[i:i + n] == phrase_tokens:
                return True
    return False
