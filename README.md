# 🖱️ AutoKlik

> **Prosty auto-kliker dla Linux** — nagrywa i powtarza ruchy myszy, kliknięcia, scrollowanie oraz klawiaturę w nieskończonej pętli. Idealny do utrzymania aktywnej sesji (np. Google Colab).

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Linux](https://img.shields.io/badge/Platform-Linux-orange?logo=linux)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Funkcje

| Funkcja | Opis |
|---|---|
| ⏺ **Nagrywanie myszy** | Ruchy, kliknięcia (LPM/PPM/środkowy), scroll |
| ⌨ **Nagrywanie klawiatury** | Wciśnięcia i puszczenia klawiszy z dokładnymi opóźnieniami |
| ▶ **Odtwarzanie w pętli** | Wierne powtarzanie nagrania w nieskończoność |
| ⏸ **Pauza między pętlami** | Regulowana przerwa (0–60 sek) |
| ☑ **Opcje nagrywania** | Włącz/wyłącz mysz i/lub klawiaturę niezależnie |
| ⌨ **ESC** | Natychmiastowe zatrzymanie nagrywania lub odtwarzania |
| 🎨 **Ciemny motyw** | Catppuccin Mocha — czytelny interfejs |

---

## 📦 Wymagania

- Python 3.8+
- `pynput` (z zależnościami: `six`, `python-xlib`)
- `tkinter` (zazwyczaj wbudowany w Python)

---

## 🚀 Instalacja

### Opcja 1 — `make install` (zalecane)

```bash
git clone https://github.com/twoj-login/autoklik.git
cd autoklik
make install
```

Instaluje zależności, kopiuje plik `.desktop` i ikonę — aplikacja pojawi się w menu systemowym.

### Opcja 2 — ręcznie

```bash
git clone https://github.com/twoj-login/autoklik.git
cd autoklik
pip install six python-xlib
pip install pynput --no-deps
python3 autoklik.py
```

---

## 🎮 Użycie

1. Uruchom aplikację (`make run` lub `python3 autoklik.py`)
2. Zaznacz co chcesz nagrywać (mysz / klawiatura)
3. Kliknij **⏺ NAGRAJ** i wykonaj czynności do powtórzenia
4. Naciśnij **ESC** — nagrywanie kończy się
5. Ustaw pauzę między pętlami (domyślnie 0.5 sek)
6. Kliknij **▶ START** — akcje powtarzają się w pętli
7. **ESC** zatrzymuje odtwarzanie

> 💡 **Tip dla Google Colab:** Nagraj np. ruch myszy po stronie i kliknięcie, ustaw pauzę 30 sek — zapobiegnie to rozłączeniu sesji.

---

## 🛠️ Komendy Makefile

```bash
make install    # Instalacja (zależności + skrót w menu)
make run        # Uruchom aplikację
make uninstall  # Odinstaluj (usuń skrót z menu)
make clean      # Usuń pliki tymczasowe (__pycache__ itp.)
```

---

## 📁 Struktura projektu

```
autoklik/
├── autoklik.py          # Główna aplikacja
├── autoklik.desktop     # Skrót do menu systemowego
├── icon.png             # Ikona aplikacji
├── Makefile             # Automatyzacja instalacji
└── README.md            # Ten plik
```

---

## ⚠️ Uwagi

- Podczas odtwarzania **nie ruszaj myszą** — kliker przejmuje kontrolę
- **ESC** nigdy nie jest nagrywany — zawsze zatrzymuje aplikację
- Działa na środowiskach X11 (Xorg). Wayland może wymagać dodatkowej konfiguracji

---

## 📄 Licencja

MIT — używaj swobodnie.
