PREFIX ?= $(HOME)/.local
APPDIR  = $(HOME)/.local/share/applications
ICONDIR = $(HOME)/.local/share/icons/hicolor/256x256/apps
SCRIPT  = $(PREFIX)/bin/autoklik
SRCDIR  = $(shell pwd)

.PHONY: all install run uninstall clean

all: run

## ── Uruchom aplikację ──────────────────────────────
run:
	python3 $(SRCDIR)/autoklik.py

## ── Instalacja ─────────────────────────────────────
install: _deps _icon _desktop _bin
	@echo ""
	@echo "✅  AutoKlik zainstalowany!"
	@echo "    Uruchom: autoklik  lub znajdź w menu aplikacji."

_deps:
	@echo "📦  Instaluję zależności Python..."
	pip3 install six python-xlib --break-system-packages --quiet 2>/dev/null || \
	pip3 install six python-xlib --quiet
	pip3 install pynput --no-deps --break-system-packages --quiet 2>/dev/null || \
	pip3 install pynput --no-deps --quiet

_icon:
	@echo "🖼   Kopiuję ikonę..."
	mkdir -p $(ICONDIR)
	cp $(SRCDIR)/icon.png $(ICONDIR)/autoklik.png

_desktop:
	@echo "🔗  Instaluję skrót w menu..."
	mkdir -p $(APPDIR)
	sed "s|SRCDIR|$(SRCDIR)|g" $(SRCDIR)/autoklik.desktop > $(APPDIR)/autoklik.desktop
	chmod +x $(APPDIR)/autoklik.desktop
	update-desktop-database $(APPDIR) 2>/dev/null || true

_bin:
	@echo "🔧  Tworzę komendę 'autoklik'..."
	mkdir -p $(PREFIX)/bin
	printf '#!/bin/bash\npython3 $(SRCDIR)/autoklik.py "$$@"\n' > $(SCRIPT)
	chmod +x $(SCRIPT)

## ── Odinstalowanie ─────────────────────────────────
uninstall:
	@echo "🗑   Odinstalowuję AutoKlik..."
	rm -f $(APPDIR)/autoklik.desktop
	rm -f $(ICONDIR)/autoklik.png
	rm -f $(SCRIPT)
	update-desktop-database $(APPDIR) 2>/dev/null || true
	@echo "✅  Gotowe."

## ── Czyszczenie ────────────────────────────────────
clean:
	find $(SRCDIR) -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find $(SRCDIR) -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅  Wyczyszczono."
