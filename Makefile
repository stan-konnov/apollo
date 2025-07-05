VENV ?= venv
PYTHON = $(VENV)/bin/python
UV = $(VENV)/bin/uv

.PHONY: help venv install

help:
	@echo ""
	@echo "Common tasks:"
	@echo "  make venv       - create a virtual environment"
	@echo "  make install    - install dependencies (including editable apollo & poe)"
	@echo ""

venv:
	@echo "🐍 Creating virtual environment in $(VENV)…"
	python3 -m venv $(VENV)
	@echo "✅ Done."

install: venv
	@echo "📦 Installing dependencies with uv…"
	. $(VENV)/bin/activate && pip install -U uv && uv pip install -r requirements.txt -e .
	@echo "✅ Installed."