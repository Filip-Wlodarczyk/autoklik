#!/usr/bin/env python3
"""
AutoKlik - Simple auto-clicker for Linux
Works on X11 and Wayland (via XWayland + xdotool).

Recording : pynput  (passive listener — no permission dialog)
Playback  : xdotool (subprocess — no Wayland remote-desktop dialog)

ESC — stop recording / stop playback
"""

import tkinter as tk
from tkinter import messagebox
import threading
import subprocess
import time
import os
import sys

from pynput import mouse
from pynput.keyboard import Key, Listener as KeyListener

# ── Catppuccin Mocha palette ───────────────────────
BG     = "#1e1e2e"
CARD   = "#313244"
CARD2  = "#45475a"
ACCENT = "#cba6f7"
GREEN  = "#a6e3a1"
RED    = "#f38ba8"
YELLOW = "#f9e2af"
BLUE   = "#89b4fa"
FG     = "#cdd6f4"
MUTED  = "#6c7086"


# ─────────────────────────────────────────────────────────────
#  xdotool helpers
# ─────────────────────────────────────────────────────────────
def _env():
    """Return environment with DISPLAY set (needed under Wayland/XWayland)."""
    e = os.environ.copy()
    if not e.get("DISPLAY"):
        e["DISPLAY"] = ":0"
    return e


def _xdo(*args):
    """Run xdotool <args>, silently ignore errors."""
    try:
        subprocess.run(["xdotool"] + list(str(a) for a in args),
                       env=_env(), capture_output=True, timeout=2)
    except Exception:
        pass


# Map pynput Key → xdotool key name
_KEY_MAP = {
    Key.space:     "space",
    Key.enter:     "Return",
    Key.backspace: "BackSpace",
    Key.tab:       "Tab",
    Key.shift:     "shift",    Key.shift_r:  "shift",
    Key.ctrl:      "ctrl",     Key.ctrl_r:   "ctrl",
    Key.alt:       "alt",      Key.alt_r:    "alt",
    Key.cmd:       "super",    Key.cmd_r:    "super",
    Key.caps_lock: "Caps_Lock",
    Key.delete:    "Delete",   Key.insert:   "Insert",
    Key.home:      "Home",     Key.end:      "End",
    Key.page_up:   "Page_Up",  Key.page_down:"Page_Down",
    Key.up:        "Up",       Key.down:     "Down",
    Key.left:      "Left",     Key.right:    "Right",
    Key.f1:  "F1",  Key.f2:  "F2",  Key.f3:  "F3",  Key.f4:  "F4",
    Key.f5:  "F5",  Key.f6:  "F6",  Key.f7:  "F7",  Key.f8:  "F8",
    Key.f9:  "F9",  Key.f10: "F10", Key.f11: "F11", Key.f12: "F12",
    Key.num_lock:  "Num_Lock",
    Key.scroll_lock: "Scroll_Lock",
    Key.print_screen: "Print",
    Key.pause:     "Pause",
    Key.esc:       "Escape",
}


def _key_to_xdo(key):
    """Convert pynput key object → xdotool key name string, or None."""
    if key in _KEY_MAP:
        return _KEY_MAP[key]
    try:
        if hasattr(key, "char") and key.char:
            # Escape special chars for xdotool
            ch = key.char
            return ch
    except Exception:
        pass
    # vk fallback
    try:
        vk = key.vk
        if vk:
            return f"0x{vk:04x}"
    except Exception:
        pass
    return None


def _key_display(key):
    """Human-readable key name for the UI."""
    try:
        if hasattr(key, "char") and key.char:
            return key.char
        return str(key).replace("Key.", "").upper()
    except Exception:
        return str(key)


# ─────────────────────────────────────────────────────────────
#  Check backends at startup
# ─────────────────────────────────────────────────────────────
def _check_xdotool():
    try:
        r = subprocess.run(["xdotool", "--version"],
                           capture_output=True, timeout=3)
        return r.returncode == 0
    except FileNotFoundError:
        return False


def _detect_session():
    """Return 'wayland', 'x11', or 'unknown'."""
    s = os.environ.get("XDG_SESSION_TYPE", "").lower()
    if s:
        return s
    if os.environ.get("WAYLAND_DISPLAY"):
        return "wayland"
    if os.environ.get("DISPLAY"):
        return "x11"
    return "unknown"


# ─────────────────────────────────────────────────────────────
#  Main application
# ─────────────────────────────────────────────────────────────
class AutoKlik:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoKlik")
        self.root.geometry("430x580")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        # ── State ──────────────────────────────────
        self.recording   = False
        self.playing     = False
        self.events      = []          # (etype, edata, delay_seconds)
        self.last_event_time = None
        self.loop_count  = 0

        # ── Options ────────────────────────────────
        self.record_mouse_var    = tk.BooleanVar(value=True)
        self.record_keyboard_var = tk.BooleanVar(value=True)
        self.delay_var           = tk.DoubleVar(value=0.5)

        # ── Listeners (recording only) ─────────────
        self.record_listener_mouse    = None
        self.record_listener_keyboard = None
        self.play_thread              = None
        self.global_key_listener      = None

        # ── Backend status ─────────────────────────
        self.xdotool_ok  = _check_xdotool()
        self.session     = _detect_session()

        self._build_ui()
        self._start_global_esc_listener()

    # ─────────────────────────────────────────────
    #  UI
    # ─────────────────────────────────────────────
    def _build_ui(self):
        # Title
        tk.Label(self.root, text="🖱️  AutoKlik",
                 font=("Segoe UI", 22, "bold"), bg=BG, fg=ACCENT).pack(pady=(18, 2))

        # Session / backend info bar
        session_color = GREEN if self.xdotool_ok else YELLOW
        session_icon  = "✅" if self.xdotool_ok else "⚠"
        xdo_status    = "xdotool ✓" if self.xdotool_ok else "xdotool MISSING — install: sudo apt install xdotool"
        tk.Label(self.root,
                 text=f"{session_icon}  Session: {self.session.upper()}   |   {xdo_status}",
                 font=("Segoe UI", 8, "bold"), bg=CARD2, fg=session_color,
                 anchor="center").pack(fill="x", padx=24, pady=(0, 12))

        # ── STEP 1 ─────────────────────────────────
        self._section_label("STEP 1 — Record actions")

        opt = self._card()
        tk.Label(opt, text="Record:", font=("Segoe UI", 9),
                 bg=CARD, fg=MUTED).pack(side="left", padx=(12, 8), pady=10)
        ck = dict(bg=CARD, fg=FG, activebackground=CARD, activeforeground=FG,
                  selectcolor=CARD2, font=("Segoe UI", 10), bd=0, relief="flat")
        tk.Checkbutton(opt, text="🖱 Mouse",    variable=self.record_mouse_var,    **ck).pack(side="left", pady=10)
        tk.Checkbutton(opt, text="⌨ Keyboard", variable=self.record_keyboard_var, **ck).pack(side="left", padx=(10, 12), pady=10)

        self.btn_record = tk.Button(
            self.root, text="⏺  START RECORDING",
            font=("Segoe UI", 13, "bold"),
            bg=RED, fg="#11111b",
            activebackground="#f5a0b8", activeforeground="#11111b",
            relief="flat", bd=0, cursor="hand2", height=2,
            command=self._toggle_record)
        self.btn_record.pack(fill="x", padx=24, pady=(4, 4))

        info1 = self._card()
        tk.Label(info1, text="Actions recorded:",
                 font=("Segoe UI", 9), bg=CARD, fg=MUTED).pack(side="left", padx=(12, 4), pady=8)
        self.events_label = tk.Label(info1, text="0",
                                     font=("Segoe UI", 11, "bold"), bg=CARD, fg=ACCENT)
        self.events_label.pack(side="left")
        tk.Label(info1, text="   Last key:", font=("Segoe UI", 9),
                 bg=CARD, fg=MUTED).pack(side="left")
        self.key_label = tk.Label(info1, text="—",
                                  font=("Segoe UI", 10, "bold"), bg=CARD, fg=YELLOW)
        self.key_label.pack(side="left", padx=(4, 12))

        # ── STEP 2 ─────────────────────────────────
        self._section_label("STEP 2 — Play back in loop")

        self.btn_play = tk.Button(
            self.root, text="▶  START PLAYBACK",
            font=("Segoe UI", 13, "bold"),
            bg=CARD2, fg=MUTED,
            activebackground="#b0f5ab", activeforeground="#11111b",
            relief="flat", bd=0, cursor="hand2", height=2,
            state="disabled",
            command=self._toggle_play)
        self.btn_play.pack(fill="x", padx=24, pady=(4, 4))

        info2 = self._card()
        tk.Label(info2, text="Loop #:", font=("Segoe UI", 9),
                 bg=CARD, fg=MUTED).pack(side="left", padx=(12, 4), pady=8)
        self.loop_label = tk.Label(info2, text="0",
                                   font=("Segoe UI", 11, "bold"), bg=CARD, fg=GREEN)
        self.loop_label.pack(side="left")
        tk.Label(info2, text="   Pause between loops (sec):",
                 font=("Segoe UI", 9), bg=CARD, fg=MUTED).pack(side="left")
        tk.Spinbox(info2, from_=0.0, to=60.0, increment=0.5,
                   textvariable=self.delay_var, width=5,
                   font=("Segoe UI", 10), bg=CARD2, fg=FG,
                   buttonbackground=CARD, relief="flat").pack(side="left", padx=(6, 12))

        # ── Status bar ─────────────────────────────
        self.status_bar = tk.Label(
            self.root,
            text="⏹  Idle — press START RECORDING to begin",
            font=("Segoe UI", 9, "bold"),
            bg=CARD2, fg=FG, anchor="w", padx=12, pady=8)
        self.status_bar.pack(fill="x", padx=24, pady=(10, 0))

        # Clear + hint
        self.btn_clear = tk.Button(
            self.root, text="🗑  Clear recording",
            font=("Segoe UI", 9), bg=CARD, fg=MUTED,
            activebackground=CARD2, activeforeground=FG,
            relief="flat", bd=0, cursor="hand2",
            command=self._clear_recording)
        self.btn_clear.pack(pady=(8, 0))

        tk.Label(self.root,
                 text="ESC  →  stop recording / stop playback",
                 font=("Segoe UI", 8), bg=BG, fg=MUTED).pack(pady=(6, 0))

    def _section_label(self, text):
        tk.Label(self.root, text=text,
                 font=("Segoe UI", 9, "bold"), bg=BG, fg=BLUE,
                 anchor="w").pack(fill="x", padx=24, pady=(10, 2))

    def _card(self):
        f = tk.Frame(self.root, bg=CARD)
        f.pack(fill="x", padx=24, pady=(0, 6))
        return f

    # ─────────────────────────────────────────────
    #  Global ESC listener — passive read only
    # ─────────────────────────────────────────────
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

    # ─────────────────────────────────────────────
    #  RECORDING
    # ─────────────────────────────────────────────
    def _toggle_record(self):
        if self.playing:
            messagebox.showwarning("AutoKlik", "Stop playback before recording!")
            return
        if self.recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        if not self.record_mouse_var.get() and not self.record_keyboard_var.get():
            messagebox.showwarning("AutoKlik",
                "Select at least one option to record\n(Mouse / Keyboard)!")
            return

        self.events.clear()
        self.recording = True
        self.last_event_time = time.time()
        self._update_ui()

        # Mouse listener
        if self.record_mouse_var.get():
            def on_move(x, y):
                if not self.recording:
                    return False
                self._append("move", (x, y))

            def on_click(x, y, button, pressed):
                if not self.recording:
                    return False
                self._append("click", (x, y, button.name, pressed))

            def on_scroll(x, y, dx, dy):
                if not self.recording:
                    return False
                self._append("scroll", (x, y, dx, dy))

            self.record_listener_mouse = mouse.Listener(
                on_move=on_move, on_click=on_click, on_scroll=on_scroll, daemon=True)
            self.record_listener_mouse.start()

        # Keyboard listener
        if self.record_keyboard_var.get():
            def on_key_press(key):
                if not self.recording:
                    return False
                if key == Key.esc:
                    return          # handled by global listener
                self._append("key_press", key)
                self.root.after(0, lambda k=key:
                    self.key_label.config(text=_key_display(k)))

            def on_key_release(key):
                if not self.recording:
                    return False
                if key == Key.esc:
                    return
                self._append("key_release", key)

            self.record_listener_keyboard = KeyListener(
                on_press=on_key_press, on_release=on_key_release, daemon=True)
            self.record_listener_keyboard.start()

    def _append(self, etype, edata):
        now = time.time()
        self.events.append((etype, edata, now - self.last_event_time))
        self.last_event_time = now
        self.root.after(0, lambda:
            self.events_label.config(text=str(len(self.events))))

    def _stop_recording(self):
        self.recording = False
        for lst in (self.record_listener_mouse, self.record_listener_keyboard):
            if lst:
                lst.stop()
        self.record_listener_mouse = None
        self.record_listener_keyboard = None
        self.root.after(0, self._update_ui)

    # ─────────────────────────────────────────────
    #  PLAYBACK  — via xdotool (X11 + Wayland safe)
    # ─────────────────────────────────────────────
    def _toggle_play(self):
        if self.recording:
            messagebox.showwarning("AutoKlik", "Stop recording before playing!")
            return
        if self.playing:
            self._stop_playing()
        else:
            self._start_playing()

    def _start_playing(self):
        if not self.events:
            messagebox.showinfo("AutoKlik",
                "No recording!\nRecord actions first (Step 1).")
            return
        if not self.xdotool_ok:
            messagebox.showerror("AutoKlik",
                "xdotool is not installed!\n\n"
                "Install it with:\n  sudo apt install xdotool\n\n"
                "xdotool is required for playback on Wayland.")
            return

        self.playing = True
        self.loop_count = 0
        self._update_ui()
        self.play_thread = threading.Thread(target=self._play_loop, daemon=True)
        self.play_thread.start()

    def _play_loop(self):
        while self.playing:
            self.loop_count += 1
            self.root.after(0, lambda n=self.loop_count:
                self.loop_label.config(text=str(n)))

            for etype, edata, delay in self.events:
                if not self.playing:
                    break

                # Interruptible wait — cap long pauses
                cap  = 2.0 if etype == "move" else 5.0
                until = time.time() + min(delay, cap)
                while self.playing and time.time() < until:
                    time.sleep(0.05)

                if not self.playing:
                    break

                try:
                    if etype == "move":
                        x, y = edata
                        _xdo("mousemove", "--sync", x, y)

                    elif etype == "click":
                        x, y, btn_name, pressed = edata
                        _xdo("mousemove", "--sync", x, y)
                        num = {"left": "1", "middle": "2", "right": "3"}.get(btn_name, "1")
                        _xdo("mousedown" if pressed else "mouseup", num)

                    elif etype == "scroll":
                        x, y, dx, dy = edata
                        _xdo("mousemove", "--sync", x, y)
                        if dy > 0:
                            _xdo("click", "--repeat", str(max(1, abs(int(dy)))), "4")
                        elif dy < 0:
                            _xdo("click", "--repeat", str(max(1, abs(int(dy)))), "5")

                    elif etype == "key_press":
                        xk = _key_to_xdo(edata)
                        if xk:
                            _xdo("keydown", xk)
                            self.root.after(0, lambda k=edata:
                                self.key_label.config(text=f"▶ {_key_display(k)}"))

                    elif etype == "key_release":
                        xk = _key_to_xdo(edata)
                        if xk:
                            _xdo("keyup", xk)

                except Exception:
                    pass

            # Pause between loops
            if self.playing:
                until = time.time() + self.delay_var.get()
                while self.playing and time.time() < until:
                    time.sleep(0.05)

        self.root.after(0, self._update_ui)

    def _stop_playing(self):
        self.playing = False

    # ─────────────────────────────────────────────
    #  Helpers
    # ─────────────────────────────────────────────
    def _clear_recording(self):
        if self.recording or self.playing:
            messagebox.showwarning("AutoKlik",
                "Stop recording / playback before clearing!")
            return
        self.events.clear()
        self.events_label.config(text="0")
        self.loop_label.config(text="0")
        self.key_label.config(text="—")
        self._update_ui()

    def _update_ui(self):
        count = len(self.events)
        self.events_label.config(text=str(count))

        if self.recording:
            self.btn_record.config(
                text="⏹  STOP RECORDING  (or press ESC)",
                bg=YELLOW, fg="#11111b", state="normal")
            self.btn_play.config(
                text="▶  START PLAYBACK",
                bg=CARD2, fg=MUTED, state="disabled")
            self.status_bar.config(
                text="⏺  Recording... press STOP or ESC when done",
                fg=RED)

        elif self.playing:
            self.btn_record.config(
                text="⏺  START RECORDING",
                bg=CARD2, fg=MUTED, state="disabled")
            self.btn_play.config(
                text="⏹  STOP PLAYBACK  (or press ESC)",
                bg=YELLOW, fg="#11111b", state="normal")
            self.status_bar.config(
                text="▶  Playing back... press STOP or ESC to stop",
                fg=GREEN)

        else:
            self.btn_record.config(
                text="⏺  START RECORDING",
                bg=RED, fg="#11111b", state="normal")
            if count > 0:
                self.btn_play.config(
                    text=f"▶  START PLAYBACK  ({count} actions recorded)",
                    bg=GREEN, fg="#11111b", state="normal")
                self.status_bar.config(
                    text=f"✅  {count} actions ready — press START PLAYBACK!",
                    fg=GREEN)
            else:
                self.btn_play.config(
                    text="▶  START PLAYBACK",
                    bg=CARD2, fg=MUTED, state="disabled")
                self.status_bar.config(
                    text="⏹  Idle — press START RECORDING to begin",
                    fg=FG)

    def on_close(self):
        self.recording = False
        self.playing   = False
        for lst in (self.global_key_listener,
                    self.record_listener_mouse,
                    self.record_listener_keyboard):
            if lst:
                lst.stop()
        self.root.destroy()


# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app  = AutoKlik(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
