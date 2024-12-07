# Name of the virtual environment
VENV_NAME = venv
# Environment variables for project configuration
export PROJECT_NAME = PostGenius
export AUTHOR = Stefano Roy Bisignano & Mirko Di Maggio
export RELEASE = 0.1
# Key paths
PYTHON = $(VENV_NAME)/bin/python
PIP = $(VENV_NAME)/bin/pip
REQ_FILE = requirements.txt
CONF_FILE = docs/conf.py
INDEX_FILE = docs/index.rst
TARGET_DIR = backend
.PHONY: all clean setup docs-setup docs-update docs-open docs-fix docs-theme readme-update tests-create tests-run activate deactivate help

# Main goal: update everything and prepare for a commit
all: docs-update reqs-update readme-update tests-create commit-push ## Update all: requirements.txt, documentation, README.md structure, create tests, and push changes.

# Show available commands
help:
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Create a virtual environment if it doesn't exist
setup: ## Create the virtual environment and update pip
	@test -d $(VENV_NAME) || python3 -m venv $(VENV_NAME)
	@$(PIP) install --upgrade pip

# Activate the virtual environment
activate: ## Activate the virtual environment (run 'source venv/bin/activate' manually if needed)
	@echo "To activate the virtual environment, run the command:"
	@echo "source $(VENV_NAME)/bin/activate"

# Deactivate the virtual environment
deactivate: ## Deactivate the virtual environment (manual deactivation)
	@echo "To deactivate the virtual environment, run the command:"
	@echo "deactivate"

# Update requirements.txt with all libraries used in the venv
reqs-update: setup ## Update requirements.txt with installed libraries
	@echo "Updating $(REQ_FILE)..."
	@$(PIP) freeze > $(REQ_FILE)
	@echo "File $(REQ_FILE) updated successfully."

# Configure Sphinx for documentation generation
docs-setup: setup ## Configure Sphinx for documentation
	@echo "Configuring Sphinx for documentation..."
	@$(PIP) install sphinx > /dev/null
	@mkdir -p docs
	@cd docs && sphinx-quickstart --quiet --project "$(PROJECT_NAME)" \
	    --author "$(AUTHOR)" \
	    --release "$(RELEASE)" \
	    --extensions "sphinx.ext.autodoc,sphinx.ext.napoleon,sphinx.ext.viewcode,sphinx.ext.githubpages" \
	    --makefile --no-batchfile
	@echo "Verifying and adding PYTHONPATH to conf.py..."
	@if ! grep -q "sys.path.insert(0, os.path.abspath('../$(TARGET_DIR)'))" $(CONF_FILE); then \
	    echo "\n# Automatically adding paths\nimport os\nimport sys\nsys.path.insert(0, os.path.abspath('../$(TARGET_DIR)'))\nsys.path.insert(0, os.path.abspath('../'))" >> $(CONF_FILE); \
		echo "\n   source/$(TARGET_DIR)" >> $(INDEX_FILE); \
	fi
	@echo "Sphinx configured successfully! You can now generate documentation with 'make docs-update'."

docs-update: docs-fix ## Regenerate documentation with Sphinx
	@echo "Updating documentation..."
	@if [ -f docs/conf.py ]; then \
	    echo "Sphinx configuration found. Regenerating..."; \
	    sphinx-apidoc -o docs/source $(TARGET_DIR)/ --force --no-toc > /dev/null; \
	    sphinx-build -b html docs docs/_build/html; \
	    if [ -d docs/_build/html ]; then \
	        echo "Documentation updated successfully. Run 'make docs-open' to open the documentation."; \
	    else \
	        echo "Error during documentation generation."; \
	    fi \
	else \
	    echo "No Sphinx configuration found. Run 'make docs-setup' to configure Sphinx."; \
	fi

docs-open: ## Open the generated HTML documentation in the default browser
	@if [ -d docs/_build/html ]; then \
	    echo "Opening the generated documentation..."; \
	    open docs/_build/html/index.html || xdg-open docs/_build/html/index.html; \
	else \
	    echo "The documentation has not been generated. Run 'make docs-update' before opening it."; \
	fi

docs-fix: ## Add missing __init__.py files to make each directory a module
	@echo "Adding missing __init__.py files..."
	@find $(TARGET_DIR) -type d ! -name "__pycache__" -exec sh -c '[ -f "{}/__init__.py" ] || touch "{}/__init__.py"' \;

docs-theme: ## Change the documentation theme
	@read -p "Enter the theme name (e.g., furo, sphinx_rtd_theme, alabaster): " theme; \
	sed -i.bak "s/^html_theme =.*/html_theme = '$$theme'/g" $(CONF_FILE); \
	echo "Theme set to $$theme."; \
	$(PIP) install $$theme > /dev/null 2>&1 || echo "Unable to install theme $$theme. Please verify it exists."; \
	make docs-update

readme-update: ## Update the repository structure in the README.md file
	@if [ ! -f $(PYTHON) ]; then \
	    echo "The virtual environment is not configured. Run 'make setup' before proceeding."; \
	    exit 1; \
	fi
	@$(PYTHON) scripts/update_structure.py

tests-create: ## Generate boilerplate test files
	@if [ ! -f $(PYTHON) ]; then \
	    echo "Virtual environment not configured. Run 'make setup' first."; \
	    exit 1; \
	fi
	@echo "Generating boilerplate test files..."
	@$(PYTHON) scripts/create_tests.py
	@echo "Test files created successfully!"

tests-run: ## Run all unit tests
	@echo "Running all unit tests..."
	@python -m unittest discover tests
	@echo "All tests completed successfully!"

clean: ## Clean up the repository by removing temporary files and the virtual environment
	@echo "Cleaning the environment..."
	@rm -rf $(VENV_NAME)
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@echo "Cleanup completed."
