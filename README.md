# 🖱️ AutoKlik

> **A simple auto-clicker for Linux** — records and replays mouse movements, clicks, scrolling, and keyboard input in an infinite loop. Perfect for keeping sessions alive (e.g. Google Colab).

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Linux](https://img.shields.io/badge/Platform-Linux-orange?logo=linux)
![X11](https://img.shields.io/badge/X11-supported-brightgreen)
![Wayland](https://img.shields.io/badge/Wayland-supported-brightgreen)
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
| 🖥️ **X11 + Wayland** | Works on both session types via xdotool |
| 🎨 **Dark theme** | Catppuccin Mocha — clean, readable UI |

---

## 📦 Requirements

| Package | Purpose |
|---|---|
| `python3` (3.8+) | Runtime |
| `tkinter` | GUI (usually bundled with Python) |
| `pynput` | Recording mouse & keyboard events |
| `six`, `python-xlib` | pynput dependencies |
| **`xdotool`** | **Playback on X11 and Wayland** |

> [!IMPORTANT]
> `xdotool` is required for playback. Without it, recording works but playback is disabled.
> On Wayland, pynput's built-in controller shows a **"Remote Desktop Access"** permission dialog — `xdotool` avoids this entirely.

---

## 🚀 Installation

### Option 1 — `make install` (recommended)

```bash
git clone https://github.com/Filip-Wlodarczyk/autoklik.git
cd autoklik
make install
```

Installs all dependencies, copies the `.desktop` entry and icon — the app appears in your system application menu.

> **Note:** You may need to log out and back in for the menu entry to appear.

### Option 2 — Manual

```bash
git clone https://github.com/Filip-Wlodarczyk/autoklik.git
cd autoklik

# Install xdotool (required for playback)
sudo apt install xdotool

# Install Python dependencies
pip install six python-xlib
pip install pynput --no-deps

# Run
python3 autoklik.py
```

---

## 🎮 How to Use

1. Launch the app (`make run` or `python3 autoklik.py`)
2. Check what to record — **🖱 Mouse** and/or **⌨ Keyboard**
3. Click **⏺ START RECORDING** and perform the actions you want to repeat
4. Press **ESC** or click **STOP RECORDING** — recording stops
5. The **▶ START PLAYBACK** button activates automatically
6. Set the pause between loops (default: 0.5 sec)
7. Click **▶ START PLAYBACK** — actions repeat in an infinite loop
8. Press **ESC** or **STOP PLAYBACK** to stop

> 💡 **Google Colab tip:** Record a simple mouse movement and click, set a 30-second loop delay — this prevents the session from disconnecting due to inactivity.

---

## 🖥️ X11 vs Wayland

| Feature | X11 | Wayland |
|---|---|---|
| Recording (pynput) | ✅ | ✅ (via XWayland) |
| Playback (xdotool) | ✅ | ✅ (via XWayland) |
| No permission dialogs | ✅ | ✅ |

AutoKlik uses `xdotool` for playback on both X11 and Wayland. On Wayland, it runs through XWayland automatically — no extra configuration needed.

---

## 🛠️ Makefile Commands

```bash
make install    # Install dependencies + add app to system menu
make run        # Launch the app directly
make uninstall  # Remove from menu and PATH
make clean      # Remove temporary files (__pycache__ etc.)
```

---

## 📁 Project Structure

```
autoklik/
├── autoklik.py          # Main application
├── autoklik.desktop     # System menu shortcut (.desktop entry)
├── icon.png             # App icon (256×256 PNG)
├── Makefile             # One-command installation
└── README.md            # This file
```

---

## ⚠️ Notes

- During playback, **avoid moving the mouse** — the app controls it
- **ESC is never recorded** — it always stops the app
- Requires **XWayland** on Wayland sessions (installed by default on most distros)
- Tested on **Ubuntu 24.04**, **Fedora 40**, **Arch Linux** with GNOME and KDE

---

## 📄 License

MIT — free to use and modify.
