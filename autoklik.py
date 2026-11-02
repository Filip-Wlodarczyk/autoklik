#!/usr/bin/env python3
"""
AutoKlik - Prosty auto-kliker dla Linux
Nagrywa ruchy myszy, kliknięcia, scrollowanie i klawiaturę, a następnie powtarza w pętli.
ESC - zatrzymuje nagrywanie / odtwarzanie
"""

import tkinter as tk
from tkinter import messagebox
import threading
import time
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, KeyCode, Controller as KeyboardController, Listener as KeyListener


class AutoKlik:
    def __init__(self, root):
        self.root = root
        self.root.title("🖱️ AutoKlik")
        self.root.geometry("400x520")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

        # Stan aplikacji
        self.recording = False
        self.playing = False
        self.events = []
        self.last_event_time = None
        self.loop_count = 0

        # Opcje nagrywania
        self.record_mouse_var = tk.BooleanVar(value=True)
        self.record_keyboard_var = tk.BooleanVar(value=True)

        # Listenersy / kontrolery
        self.record_listener_mouse = None
        self.record_listener_keyboard = None
        self.play_thread = None
        self.global_key_listener = None

        self.mouse_ctrl = MouseController()
        self.kbd_ctrl = KeyboardController()

        self._build_ui()
        self._start_global_esc_listener()

    # ──────────────────────────────────────────────
    # UI
    # ──────────────────────────────────────────────
    def _build_ui(self):
        BG    = "#1e1e2e"
        CARD  = "#313244"
        ACCENT= "#cba6f7"
        GREEN = "#a6e3a1"
        RED   = "#f38ba8"
        YELLOW= "#f9e2af"
        FG    = "#cdd6f4"
        MUTED = "#6c7086"

        # ── Tytuł ──
        tk.Label(self.root, text="🖱️  AutoKlik", font=("Segoe UI", 20, "bold"),
                 bg=BG, fg=ACCENT).pack(pady=(18, 2))
        tk.Label(self.root, text="Nagrywaj i powtarzaj akcje myszy i klawiatury",
                 font=("Segoe UI", 9), bg=BG, fg=MUTED).pack(pady=(0, 12))

        # ── Opcje nagrywania ──
        opt_frame = tk.Frame(self.root, bg=CARD)
        opt_frame.pack(fill="x", padx=24, pady=(0, 10))
        tk.Label(opt_frame, text="Nagrywaj:", font=("Segoe UI", 9, "bold"),
                 bg=CARD, fg=MUTED).pack(side="left", padx=(12, 10), pady=10)

        chk_style = dict(bg=CARD, fg=FG, activebackground=CARD, activeforeground=FG,
                         selectcolor="#45475a", font=("Segoe UI", 9), bd=0, relief="flat")
        tk.Checkbutton(opt_frame, text="🖱 Mysz", variable=self.record_mouse_var,
                       **chk_style).pack(side="left", pady=10)
        tk.Checkbutton(opt_frame, text="⌨ Klawiatura", variable=self.record_keyboard_var,
                       **chk_style).pack(side="left", padx=(8, 12), pady=10)

        # ── Karta statusu ──
        status_frame = tk.Frame(self.root, bg=CARD)
        status_frame.pack(fill="x", padx=24, pady=(0, 10))
        tk.Label(status_frame, text="Status:", font=("Segoe UI", 9),
                 bg=CARD, fg=MUTED).pack(side="left", padx=(12, 4), pady=10)
        self.status_label = tk.Label(status_frame, text="⏹  Bezczynny",
                                     font=("Segoe UI", 10, "bold"), bg=CARD, fg=FG)
        self.status_label.pack(side="left", pady=10)

        # ── Liczniki ──
        info_frame = tk.Frame(self.root, bg=CARD)
        info_frame.pack(fill="x", padx=24, pady=(0, 12))
        tk.Label(info_frame, text="Nagrane akcje:", font=("Segoe UI", 9),
                 bg=CARD, fg=MUTED).pack(side="left", padx=(12, 4), pady=8)
        self.events_label = tk.Label(info_frame, text="0",
                                     font=("Segoe UI", 10, "bold"), bg=CARD, fg=ACCENT)
        self.events_label.pack(side="left", pady=8)
        tk.Label(info_frame, text="  |  Pętla #:", font=("Segoe UI", 9),
                 bg=CARD, fg=MUTED).pack(side="left", pady=8)
        self.loop_label = tk.Label(info_frame, text="0",
                                   font=("Segoe UI", 10, "bold"), bg=CARD, fg=GREEN)
        self.loop_label.pack(side="left", pady=8)

        # ── Ostatni klawisz ──
        key_frame = tk.Frame(self.root, bg=CARD)
        key_frame.pack(fill="x", padx=24, pady=(0, 12))
        tk.Label(key_frame, text="Ostatni klawisz:", font=("Segoe UI", 9),
                 bg=CARD, fg=MUTED).pack(side="left", padx=(12, 4), pady=8)
        self.key_label = tk.Label(key_frame, text="—",
                                  font=("Segoe UI", 10, "bold"), bg=CARD, fg=YELLOW)
        self.key_label.pack(side="left", pady=8)

        # ── Przycisk NAGRAJ ──
        self.btn_record = tk.Button(
            self.root, text="⏺  NAGRAJ", font=("Segoe UI", 13, "bold"),
            bg=RED, fg="#11111b", activebackground="#f5a0b8", activeforeground="#11111b",
            relief="flat", bd=0, cursor="hand2", height=2,
            command=self._toggle_record
        )
        self.btn_record.pack(fill="x", padx=24, pady=(0, 10))

        # ── Przycisk START ──
        self.btn_play = tk.Button(
            self.root, text="▶  START", font=("Segoe UI", 13, "bold"),
            bg=GREEN, fg="#11111b", activebackground="#b0f5ab", activeforeground="#11111b",
            relief="flat", bd=0, cursor="hand2", height=2,
            command=self._toggle_play
        )
        self.btn_play.pack(fill="x", padx=24, pady=(0, 10))

        # ── Przycisk WYCZYŚĆ ──
        self.btn_clear = tk.Button(
            self.root, text="🗑  WYCZYŚĆ NAGRANIE", font=("Segoe UI", 10),
            bg=CARD, fg=MUTED, activebackground="#45475a", activeforeground=FG,
            relief="flat", bd=0, cursor="hand2", height=1,
            command=self._clear_recording
        )
        self.btn_clear.pack(fill="x", padx=24, pady=(0, 14))

        # ── Opóźnienie między pętlami ──
        delay_frame = tk.Frame(self.root, bg=CARD)
        delay_frame.pack(fill="x", padx=24, pady=(0, 10))
        tk.Label(delay_frame, text="Pauza między pętlami (sek):",
                 font=("Segoe UI", 9), bg=CARD, fg=MUTED).pack(side="left", padx=(12, 8), pady=8)
        self.delay_var = tk.DoubleVar(value=0.5)
        tk.Spinbox(delay_frame, from_=0.0, to=60.0, increment=0.5,
                   textvariable=self.delay_var, width=6,
                   font=("Segoe UI", 10), bg="#45475a", fg=FG,
                   buttonbackground=CARD, relief="flat").pack(side="left", pady=8)

        # ── Podpowiedź ──
        tk.Label(self.root,
                 text="ESC  →  zatrzymaj nagrywanie / odtwarzanie",
                 font=("Segoe UI", 8), bg=BG, fg=MUTED).pack(pady=(4, 0))

    # ──────────────────────────────────────────────
    # Globalny listener ESC
    # ──────────────────────────────────────────────
    def _start_global_esc_listener(self):
        def on_press(key):
            if key == Key.esc:
                self._on_esc()

        self.global_key_listener = KeyListener(on_press=on_press, daemon=True)
        self.global_key_listener.start()

    def _on_esc(self):
        if self.recording:
            self.root.after(0, self._stop_recording)
        elif self.playing:
            self.root.after(0, self._stop_playing)

    # ──────────────────────────────────────────────
    # NAGRYWANIE
    # ──────────────────────────────────────────────
    def _toggle_record(self):
        if self.playing:
            messagebox.showwarning("AutoKlik", "Zatrzymaj odtwarzanie przed nagrywaniem!")
            return
        if self.recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        if not self.record_mouse_var.get() and not self.record_keyboard_var.get():
            messagebox.showwarning("AutoKlik", "Zaznacz co najmniej jedną opcję nagrywania!")
            return

        self.events.clear()
        self.recording = True
        self.last_event_time = time.time()
        self._update_ui()

        # ── Listener myszy ──
        if self.record_mouse_var.get():
            def on_move(x, y):
                if not self.recording:
                    return False
                self._append_event("move", (x, y))

            def on_click(x, y, button, pressed):
                if not self.recording:
                    return False
                self._append_event("click", (x, y, button, pressed))

            def on_scroll(x, y, dx, dy):
                if not self.recording:
                    return False
                self._append_event("scroll", (x, y, dx, dy))

            self.record_listener_mouse = mouse.Listener(
                on_move=on_move, on_click=on_click, on_scroll=on_scroll, daemon=True)
            self.record_listener_mouse.start()

        # ── Listener klawiatury ──
        if self.record_keyboard_var.get():
            def on_key_press(key):
                if not self.recording:
                    return False
                if key == Key.esc:
                    return  # ESC obsługuje globalny listener
                self._append_event("key_press", key)
                # Pokaż ostatni klawisz w UI
                self.root.after(0, lambda k=key: self.key_label.config(
                    text=self._key_name(k)))

            def on_key_release(key):
                if not self.recording:
                    return False
                if key == Key.esc:
                    return
                self._append_event("key_release", key)

            self.record_listener_keyboard = KeyListener(
                on_press=on_key_press, on_release=on_key_release, daemon=True)
            self.record_listener_keyboard.start()

    def _append_event(self, etype, edata):
        now = time.time()
        delay = now - self.last_event_time
        self.events.append((etype, edata, delay))
        self.last_event_time = now
        self.root.after(0, lambda: self.events_label.config(text=str(len(self.events))))

    def _stop_recording(self):
        self.recording = False
        if self.record_listener_mouse:
            self.record_listener_mouse.stop()
            self.record_listener_mouse = None
        if self.record_listener_keyboard:
            self.record_listener_keyboard.stop()
            self.record_listener_keyboard = None
        self._update_ui()

    # ──────────────────────────────────────────────
    # ODTWARZANIE
    # ──────────────────────────────────────────────
    def _toggle_play(self):
        if self.recording:
            messagebox.showwarning("AutoKlik", "Zatrzymaj nagrywanie przed odtwarzaniem!")
            return
        if self.playing:
            self._stop_playing()
        else:
            self._start_playing()

    def _start_playing(self):
        if not self.events:
            messagebox.showinfo("AutoKlik", "Brak nagrania! Najpierw nagraj akcje.")
            return
        self.playing = True
        self.loop_count = 0
        self._update_ui()
        self.play_thread = threading.Thread(target=self._play_loop, daemon=True)
        self.play_thread.start()

    def _play_loop(self):
        while self.playing:
            self.loop_count += 1
            self.root.after(0, lambda lc=self.loop_count: self.loop_label.config(text=str(lc)))

            for event in self.events:
                if not self.playing:
                    break
                etype, edata, delay = event

                # Ogranicz delay (ruchy myszy max 2s, reszta max 5s)
                cap = 2.0 if etype == "move" else 5.0
                wait = min(delay, cap)
                if wait > 0:
                    # Przerywalne czekanie (sprawdzamy co 50ms)
                    end = time.time() + wait
                    while self.playing and time.time() < end:
                        time.sleep(0.05)

                if not self.playing:
                    break

                try:
                    if etype == "move":
                        self.mouse_ctrl.position = (edata[0], edata[1])
                    elif etype == "click":
                        x, y, button, pressed = edata
                        self.mouse_ctrl.position = (x, y)
                        if pressed:
                            self.mouse_ctrl.press(button)
                        else:
                            self.mouse_ctrl.release(button)
                    elif etype == "scroll":
                        x, y, dx, dy = edata
                        self.mouse_ctrl.position = (x, y)
                        self.mouse_ctrl.scroll(dx, dy)
                    elif etype == "key_press":
                        self.kbd_ctrl.press(edata)
                        # Pokaż klawisz w UI
                        self.root.after(0, lambda k=edata: self.key_label.config(
                            text=f"▶ {self._key_name(k)}"))
                    elif etype == "key_release":
                        self.kbd_ctrl.release(edata)
                except Exception:
                    pass

            # Pauza między pętlami (przerywalna)
            if self.playing:
                pause = self.delay_var.get()
                end = time.time() + pause
                while self.playing and time.time() < end:
                    time.sleep(0.05)

        self.root.after(0, self._update_ui)

    def _stop_playing(self):
        self.playing = False
        # _update_ui wywoła się przez wątek gdy skończy

    # ──────────────────────────────────────────────
    # POMOCNICZE
    # ──────────────────────────────────────────────
    def _key_name(self, key):
        """Zwraca czytelną nazwę klawisza."""
        try:
            if hasattr(key, 'char') and key.char:
                return key.char
            return str(key).replace("Key.", "").upper()
        except Exception:
            return str(key)

    def _clear_recording(self):
        if self.recording or self.playing:
            messagebox.showwarning("AutoKlik", "Zatrzymaj nagrywanie/odtwarzanie przed wyczyszczeniem!")
            return
        self.events.clear()
        self.events_label.config(text="0")
        self.loop_label.config(text="0")
        self.key_label.config(text="—")

    def _update_ui(self):
        RED    = "#f38ba8"
        GREEN  = "#a6e3a1"
        YELLOW = "#f9e2af"
        FG     = "#cdd6f4"

        if self.recording:
            self.status_label.config(text="⏺  Nagrywam... (ESC aby skończyć)", fg=RED)
            self.btn_record.config(text="⏹  STOP NAGRYWANIA", bg=YELLOW, state="normal")
            self.btn_play.config(state="disabled", bg="#45475a")
        elif self.playing:
            self.status_label.config(text="▶  Odtwarzam... (ESC aby skończyć)", fg=GREEN)
            self.btn_record.config(state="disabled", bg="#45475a")
            self.btn_play.config(text="⏹  STOP", bg=YELLOW, state="normal")
        else:
            self.status_label.config(text="⏹  Bezczynny", fg=FG)
            self.btn_record.config(text="⏺  NAGRAJ", bg=RED, state="normal")
            self.btn_play.config(text="▶  START", bg=GREEN, state="normal")
        self.events_label.config(text=str(len(self.events)))

    def on_close(self):
        self.recording = False
        self.playing = False
        if self.global_key_listener:
            self.global_key_listener.stop()
        if self.record_listener_mouse:
            self.record_listener_mouse.stop()
        if self.record_listener_keyboard:
            self.record_listener_keyboard.stop()
        self.root.destroy()


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = AutoKlik(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
