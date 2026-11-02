# 🖱️ AutoKlik

> **A simple auto-clicker for Linux** — records and replays mouse movements, clicks, scrolling, and keyboard input in an infinite loop. Perfect for keeping sessions alive (e.g. Google Colab).

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Linux](https://img.shields.io/badge/Platform-Linux-orange?logo=linux)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

| Feature | Description |
|---|---|
| ⏺ **Mouse recording** | Movements, clicks (left/right/middle), scrolling |
| ⌨ **Keyboard recording** | Key presses and releases with accurate timing |
| ▶ **Loop playback** | Faithful repetition of the recording indefinitely |
| ⏸ **Loop delay** | Adjustable pause between loops (0–60 sec) |
| ☑ **Recording options** | Enable/disable mouse and/or keyboard independently |
| ⌨ **ESC key** | Instantly stops recording or playback |
| 🎨 **Dark theme** | Catppuccin Mocha — clean, readable UI |

---

## 📦 Requirements

- Python 3.8+
- `pynput` (with dependencies: `six`, `python-xlib`)
- `tkinter` (usually bundled with Python)

---

## 🚀 Installation

### Option 1 — `make install` (recommended)

```bash
git clone https://github.com/your-username/autoklik.git
cd autoklik
make install
```

Installs dependencies, copies the `.desktop` entry and icon — the app will appear in your system application menu.

> **Note:** You may need to log out and back in (or restart your desktop session) for the app to appear in the menu.

### Option 2 — Manual

```bash
git clone https://github.com/your-username/autoklik.git
cd autoklik
pip install six python-xlib
pip install pynput --no-deps
python3 autoklik.py
```

---

## 🎮 How to Use

1. Launch the app (`make run` or `python3 autoklik.py`)
2. Check what you want to record — **Mouse** and/or **Keyboard**
3. Click **⏺ RECORD** and perform the actions you want to repeat
4. Press **ESC** — recording stops
5. Set the pause between loops (default: 0.5 sec)
6. Click **▶ START** — actions repeat in an infinite loop
7. Press **ESC** to stop playback

> 💡 **Google Colab tip:** Record a simple mouse movement and click, set a 30-second loop delay — this prevents the session from disconnecting due to inactivity.

---

## 🛠️ Makefile Commands

```bash
make install    # Install dependencies + add app to menu
make run        # Launch the app directly
make uninstall  # Remove from menu and PATH
make clean      # Remove temporary files (__pycache__ etc.)
```

---

## 📁 Project Structure

```
autoklik/
├── autoklik.py          # Main application
├── autoklik.desktop     # System menu shortcut
├── icon.png             # App icon (256×256)
├── Makefile             # One-command installation
└── README.md            # This file
```

---

## ⚠️ Notes

- During playback, **avoid moving the mouse** — the app takes control of it
- **ESC is never recorded** — it always stops the app
- Works on **X11 (Xorg)**. Wayland may require additional configuration (e.g. `xhost` or running under XWayland)

---

## 📄 License

MIT — free to use and modify.
