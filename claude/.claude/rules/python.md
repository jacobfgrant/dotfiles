---
paths:
  - "**/*.py"
  - "**/pyproject.toml"
  - "**/requirements.txt"
---

# Python Conventions

- Modern Python (3.12+ unless the project pins otherwise): use type hints
- f-strings and pathlib over `.format()`/`%` or `os.path`
- Prefer dataclasses for simple structured data (Pydantic when validation matters)
- pytest for testing, ruff for linting and formatting
- Docstrings: Brief one-liners describing what a function does. Skip the parameter/return documentation—it gets stale during development and the type hints cover it.
- Prefer stdlib over external dependencies, but well-maintained libraries are fine, especially when they're best practice (requests, boto3, etc.). Don't add a dependency to save seven lines of code.
