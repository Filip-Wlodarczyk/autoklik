PREFIX ?= $(HOME)/.local
APPDIR  = $(HOME)/.local/share/applications
ICONDIR = $(HOME)/.local/share/icons/hicolor/256x256/apps
SCRIPT  = $(PREFIX)/bin/autoklik
SRCDIR  := $(shell pwd)

.PHONY: all install run uninstall clean

all: run

## ── Run the app ────────────────────────────────────
run:
	python3 "$(SRCDIR)/autoklik.py"

## ── Install ────────────────────────────────────────
install: _deps _icon _desktop _bin
	@echo ""
	@echo "✅  AutoKlik installed!"
	@echo "    Run with: autoklik   or find it in your app menu."
	@echo "    (You may need to log out and back in for the menu entry to appear.)"

_deps:
	@echo "📦  Installing Python dependencies..."
	@pip3 install six python-xlib --break-system-packages -q 2>/dev/null || pip3 install six python-xlib -q
	@pip3 install pynput --no-deps --break-system-packages -q 2>/dev/null || pip3 install pynput --no-deps -q
	@echo "    Dependencies OK."

_icon:
	@echo "🖼   Installing icon..."
	@mkdir -p "$(ICONDIR)"
	@cp "$(SRCDIR)/icon.png" "$(ICONDIR)/autoklik.png"
	@gtk-update-icon-cache -f -t "$(HOME)/.local/share/icons/hicolor" 2>/dev/null || true
	@echo "    Icon OK."

_desktop:
	@echo "🔗  Installing desktop entry..."
	@mkdir -p "$(APPDIR)"
	@sed "s|SRCDIR|$(SRCDIR)|g" "$(SRCDIR)/autoklik.desktop" > "$(APPDIR)/autoklik.desktop"
	@chmod 644 "$(APPDIR)/autoklik.desktop"
	@update-desktop-database "$(APPDIR)" 2>/dev/null || true
	@xdg-desktop-menu forceupdate 2>/dev/null || true
	@echo "    Desktop entry OK: $(APPDIR)/autoklik.desktop"
	@echo "    Exec line: $$(grep '^Exec' $(APPDIR)/autoklik.desktop)"

_bin:
	@echo "🔧  Creating 'autoklik' command..."
	@mkdir -p "$(PREFIX)/bin"
	@printf '#!/bin/bash\nexec python3 "$(SRCDIR)/autoklik.py" "$$@"\n' > "$(SCRIPT)"
	@chmod +x "$(SCRIPT)"
	@echo "    Command OK: $(SCRIPT)"

## ── Uninstall ──────────────────────────────────────
uninstall:
	@echo "🗑   Uninstalling AutoKlik..."
	@rm -f "$(APPDIR)/autoklik.desktop"
	@rm -f "$(ICONDIR)/autoklik.png"
	@rm -f "$(SCRIPT)"
	@update-desktop-database "$(APPDIR)" 2>/dev/null || true
	@echo "✅  Done."

## ── Clean ──────────────────────────────────────────
clean:
	@find "$(SRCDIR)" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find "$(SRCDIR)" -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅  Cleaned."
