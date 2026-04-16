# Python Conventions

- Python 3.12+, managed exclusively via uv (never call pip directly)
- Type hints required on all public functions and methods
- Formatter: ruff format (replaces black)
- Linter: ruff check (replaces flake8/isort)
- Line length: 88 characters
- Imports sorted: stdlib → third-party → local (handled by ruff)
