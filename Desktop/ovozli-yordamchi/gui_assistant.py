"""Google Assistant uslubidagi kichik oynacha - ekran pastida doim ko'rinib
turadi. Buyruqni yozib yuborish ham, mikrofon tugmasi bilan gapirish ham,
"kompyuter" uyg'otuvchi so'zini aytish ham mumkin.

Ishga tushirish:
    python gui_assistant.py
"""

import ctypes
import queue
import threading
import time
import tkinter as tk
from tkinter import font as tkfont

import pyttsx3
import speech_recognition as sr

import ai_router
import config
from commands import dispatch
from voice import configure_voice
from wakeword import wake_word_detected

WIDTH = 540
HEIGHT = 92
READY_STATUS = "\U0001F916 Готов. Скажите \"компьютер\" или напишите здесь"

COLOR_IDLE = "#9aa0a6"
COLOR_LISTENING = "#8ab4f8"
COLOR_REPLY = "#e8eaed"
COLOR_ERROR = "#f28b82"

COLOR_MIC_IDLE = "#8ab4f8"
COLOR_MIC_ACTIVE = "#ea4335"


class AssistantWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hey Computer")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.97)
        self.root.configure(bg="#202124")
        self._position_window()
        self._build_ui()
        self._round_corners()

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

        accent = tk.Frame(self.root, bg="#8ab4f8", height=3)
        accent.pack(fill="x", side="top")

        top_row = tk.Frame(self.root, bg="#202124")
        top_row.pack(fill="x", padx=16, pady=(10, 0))

        self.status_var = tk.StringVar(value=READY_STATUS)
        self.status_label = tk.Label(
            top_row, textvariable=self.status_var, bg="#202124", fg="#9aa0a6",
            font=status_font, anchor="w",
        )
        self.status_label.pack(side="left", fill="x", expand=True)
        self.status_label.bind("<ButtonPress-1>", self._start_drag)
        self.status_label.bind("<B1-Motion>", self._on_drag)

        close_btn = tk.Button(
            top_row, text="✕", command=self.root.destroy, bg="#202124",
            fg="#9aa0a6", activebackground="#202124", activeforeground="#e8eaed",
            relief="flat", bd=0, font=status_font, cursor="hand2",
        )
        close_btn.pack(side="right")

        row = tk.Frame(self.root, bg="#202124")
        row.pack(fill="x", padx=16, pady=(6, 14))

        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(
            row, textvariable=self.entry_var, font=entry_font, bg="#303134",
            fg="#e8eaed", insertbackground="#e8eaed", relief="flat",
            highlightthickness=1, highlightbackground="#3c4043", highlightcolor="#8ab4f8",
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 10))
        self.entry.bind("<Return>", self._on_submit_text)

        self.mic_button = tk.Button(
            row, text="\U0001F3A4", font=("Segoe UI", 14), bg=COLOR_MIC_IDLE,
            fg="#202124", activebackground=COLOR_MIC_IDLE, relief="flat",
            command=self._on_mic_click, width=3, cursor="hand2",
        )
        self.mic_button.pack(side="right")

    def _round_corners(self):
        # Windows 11'da oyna burchaklarini yumaloqlashtiradi. Windows 10'da
        # bu DWM atributi mavjud emas, shuning uchun xato bo'lsa e'tiborsiz
        # qoldiramiz - oyna oddiy to'rtburchak bo'lib qoladi.
        try:
            hwnd = self.root.winfo_id()
            DWMWA_WINDOW_CORNER_PREFERENCE = 33
            DWMWCP_ROUND = 2
            pref = ctypes.c_int(DWMWCP_ROUND)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_WINDOW_CORNER_PREFERENCE, ctypes.byref(pref), ctypes.sizeof(pref)
            )
        except (AttributeError, OSError):
            pass

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
                item = self.command_queue.get_nowait()
                if item[0] == "status":
                    _, text, color = item
                    self.status_var.set(text)
                    self.status_label.configure(fg=color)
                elif item[0] == "mic_color":
                    _, color = item
                    self.mic_button.configure(bg=color, activebackground=color)
        except queue.Empty:
            pass
        self.root.after(100, self._poll_queue)

    def _set_status(self, text, color=COLOR_IDLE):
        self.command_queue.put(("status", text, color))

    def _set_mic_color(self, color):
        self.command_queue.put(("mic_color", color))

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
        self._set_status(f"Вы: {text}", COLOR_REPLY)

        def speak_and_show(reply):
            self._set_status(reply, COLOR_REPLY)
            self.speak(reply)

        def confirm_listen():
            return self._listen(timeout=5, phrase_time_limit=4)

        try:
            if ai_router.is_configured():
                ai_router.handle(text, speak_and_show, confirm_listen)
            else:
                dispatch(text, speak_and_show, confirm_listen)
        except Exception as exc:  # noqa: BLE001 - buyruq turlari xilma-xil, biror xato butun yordamchini o'chirib qo'ymasligi kerak
            self._set_status(f"Ошибка: {exc}", COLOR_ERROR)
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
        self._set_mic_color(COLOR_MIC_ACTIVE)
        try:
            self._set_status("Слушаю...", COLOR_LISTENING)
            text = self._listen(timeout=5, phrase_time_limit=6)
            if text:
                self._dispatch_and_report(text)
            else:
                self._set_status("Не расслышал, повторите", COLOR_ERROR)
                threading.Timer(2.5, lambda: self._set_status(READY_STATUS)).start()
        finally:
            self.busy.clear()
            self._set_mic_color(COLOR_MIC_IDLE)

    # ---------- Fonda uyg'otuvchi so'zni kutish ----------

    def _wake_word_loop(self):
        with self.mic_lock:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
        while True:
            if self.busy.is_set():
                time.sleep(0.2)
                continue
            heard = self._listen(timeout=4, phrase_time_limit=4)
            if not heard or not wake_word_detected(heard.lower(), config.WAKE_WORDS):
                continue

            self.busy.set()
            self._set_mic_color(COLOR_MIC_ACTIVE)
            try:
                self._set_status("Слушаю...", COLOR_LISTENING)
                command_text = self._listen(timeout=5, phrase_time_limit=6)
                if command_text:
                    self._dispatch_and_report(command_text)
                else:
                    self._set_status(READY_STATUS)
            finally:
                self.busy.clear()
                self._set_mic_color(COLOR_MIC_IDLE)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    AssistantWindow().run()
