PYTHON := .venv/Scripts/python.exe
PIP := .venv/Scripts/pip.exe
PRE_COMMIT := .venv/Scripts/pre-commit.exe
UVICORN := .venv/Scripts/uvicorn.exe

.PHONY: setup install hooks run check

setup: install hooks

install:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

hooks:
	$(PRE_COMMIT) install --hook-type commit-msg

run:
	$(UVICORN) main:app --reload

check:
	$(PRE_COMMIT) run --all-files
