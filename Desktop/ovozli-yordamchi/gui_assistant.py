"""Google Assistant uslubidagi kichik oynacha - ekran pastida doim ko'rinib
turadi. Buyruqni yozib yuborish ham, mikrofon tugmasi bilan gapirish ham,
"kompyuter" uyg'otuvchi so'zini aytish ham mumkin.

Ishga tushirish:
    python gui_assistant.py
"""

import queue
import threading
import time
import tkinter as tk
from tkinter import font as tkfont

import pyttsx3
import speech_recognition as sr

import config
from commands import dispatch
from voice import configure_voice

WIDTH = 520
HEIGHT = 90
READY_STATUS = "Tayyor. \"kompyuter\" deb ayting yoki bu yerga yozing"


class AssistantWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Ovozli yordamchi")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#202124")
        self._position_window()
        self._build_ui()

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        configure_voice(self.tts_engine)

        self.mic_lock = threading.Lock()
        self.busy = threading.Event()
        self.command_queue = queue.Queue()
        self.root.after(100, self._poll_queue)

        threading.Thread(target=self._wake_word_loop, daemon=True).start()

    # ---------- UI qurish ----------

    def _position_window(self):
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - WIDTH) // 2
        y = screen_h - HEIGHT - 60
        self.root.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")

    def _build_ui(self):
        status_font = tkfont.Font(family="Segoe UI", size=10)
        entry_font = tkfont.Font(family="Segoe UI", size=13)

        top_row = tk.Frame(self.root, bg="#202124")
        top_row.pack(fill="x", padx=16, pady=(8, 0))

        self.status_var = tk.StringVar(value=READY_STATUS)
        self.status_label = tk.Label(
            top_row, textvariable=self.status_var, bg="#202124", fg="#9aa0a6",
            font=status_font, anchor="w",
        )
        self.status_label.pack(side="left", fill="x", expand=True)
        self.status_label.bind("<ButtonPress-1>", self._start_drag)
        self.status_label.bind("<B1-Motion>", self._on_drag)

        close_btn = tk.Button(
            top_row, text="x", command=self.root.destroy, bg="#202124",
            fg="#9aa0a6", relief="flat", bd=0, font=status_font,
        )
        close_btn.pack(side="right")

        row = tk.Frame(self.root, bg="#202124")
        row.pack(fill="x", padx=16, pady=(4, 12))

        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(
            row, textvariable=self.entry_var, font=entry_font, bg="#303134",
            fg="#e8eaed", insertbackground="#e8eaed", relief="flat",
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))
        self.entry.bind("<Return>", self._on_submit_text)

        self.mic_button = tk.Button(
            row, text="\U0001F3A4", font=("Segoe UI", 14), bg="#8ab4f8",
            fg="#202124", relief="flat", command=self._on_mic_click, width=3,
        )
        self.mic_button.pack(side="right")

    def _start_drag(self, event):
        self._drag_offset = (event.x, event.y)

    def _on_drag(self, event):
        x = self.root.winfo_pointerx() - self._drag_offset[0]
        y = self.root.winfo_pointery() - self._drag_offset[1]
        self.root.geometry(f"+{x}+{y}")

    def speak(self, text):
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    # ---------- Asosiy oqim (thread-safe navbat orqali UI yangilanadi) ----------

    def _poll_queue(self):
        try:
            while True:
                kind, payload = self.command_queue.get_nowait()
                if kind == "status":
                    self.status_var.set(payload)
        except queue.Empty:
            pass
        self.root.after(100, self._poll_queue)

    def _set_status(self, text):
        self.command_queue.put(("status", text))

    def _listen(self, timeout=5, phrase_time_limit=6):
        # Mikrofon bir vaqtning o'zida faqat bitta joydan (uyg'otuvchi so'z
        # tsikli, mikrofon tugmasi yoki matn orqali tasdiqlash) ishlatilishi
        # kerak, aks holda SpeechRecognition xato beradi. Shu sababli
        # navbatga qo'yamiz.
        with self.mic_lock:
            with self.microphone as source:
                try:
                    audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                except sr.WaitTimeoutError:
                    return ""
        try:
            return self.recognizer.recognize_google(audio, language=config.LANGUAGE)
        except (sr.UnknownValueError, sr.RequestError):
            return ""

    def _dispatch_and_report(self, text):
        self._set_status(f"Siz: {text}")

        def speak_and_show(reply):
            self._set_status(reply)
            self.speak(reply)

        def confirm_listen():
            return self._listen(timeout=5, phrase_time_limit=4)

        dispatch(text, speak_and_show, confirm_listen)
        threading.Timer(4.0, lambda: self._set_status(READY_STATUS)).start()

    # ---------- Matn orqali buyruq ----------

    def _on_submit_text(self, _event=None):
        text = self.entry_var.get().strip()
        if not text or self.busy.is_set():
            return
        self.entry_var.set("")
        threading.Thread(target=self._run_busy, args=(text,), daemon=True).start()

    def _run_busy(self, text):
        self.busy.set()
        try:
            self._dispatch_and_report(text)
        finally:
            self.busy.clear()

    # ---------- Mikrofon tugmasi orqali buyruq ----------

    def _on_mic_click(self):
        if self.busy.is_set():
            return
        threading.Thread(target=self._voice_command_flow, daemon=True).start()

    def _voice_command_flow(self):
        self.busy.set()
        try:
            self._set_status("Tinglayapman...")
            text = self._listen(timeout=5, phrase_time_limit=6)
            if text:
                self._dispatch_and_report(text)
            else:
                self._set_status("Eshitmadim, qaytadan urinib ko'ring")
                threading.Timer(2.5, lambda: self._set_status(READY_STATUS)).start()
        finally:
            self.busy.clear()

    # ---------- Fonda uyg'otuvchi so'zni kutish ----------

    def _wake_word_loop(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        while True:
            if self.busy.is_set():
                time.sleep(0.2)
                continue
            heard = self._listen(timeout=4, phrase_time_limit=4)
            if not heard or not any(w in heard.lower() for w in config.WAKE_WORDS):
                continue

            self.busy.set()
            try:
                self._set_status("Eshityapman...")
                command_text = self._listen(timeout=5, phrase_time_limit=6)
                if command_text:
                    self._dispatch_and_report(command_text)
                else:
                    self._set_status(READY_STATUS)
            finally:
                self.busy.clear()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    AssistantWindow().run()
