# Makefile for Python backend

.PHONY: venv install run clean

# Location for the virtualenv
VENV_DIR = backends/py/venv
# The Python interpreter inside the virtualenv
PYTHON = $(VENV_DIR)/bin/python
# The pip executable inside the virtualenv
PIP = $(VENV_DIR)/bin/pip

# Create the virtual environment if it doesn't exist
venv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Creating virtual environment in $(VENV_DIR)"; \
		python3 -m venv $(VENV_DIR); \
	else \
		echo "Virtual environment already exists."; \
	fi

# (Optional) Install dependencies if a requirements.txt exists
install: venv
	@if [ -f backends/py/requirements.txt ]; then \
		echo "Installing dependencies..."; \
		$(PIP) install -r backends/py/requirements.txt; \
	else \
		echo "No requirements.txt found. Skipping dependency installation."; \
	fi

# Run the main Python script in different modes
run-py: venv
	$(PYTHON) backends/py/main.py samples/pl/hello.pl_lang --interpret

parse-py: venv
	$(PYTHON) backends/py/main.py samples/pl/hello.pl_lang --parse

compile-py: venv
	$(PYTHON) backends/py/main.py samples/pl/hello.pl_lang --compile

repl-py: venv
	$(PYTHON) backends/py/main.py --repl

test-py: venv
	$(PYTHON) backends/py/tests.py

# Clean up the virtual environment (use with caution)
clean:
	rm -rf $(VENV_DIR)
