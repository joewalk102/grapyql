# grapyql

A GraphQL client library for Python that provides a Pythonic interface for building and executing GraphQL queries and mutations.

## Project Structure

```
src/grapyql/         # Main package source
  __init__.py        # Exports Field, GqlObject, Function, Query, Mutation
  client.py          # Client class for executing queries/mutations via HTTP
  components.py      # Field, GqlObject, Function classes
  operations.py      # Query, Mutation root operation classes
  errors.py          # GraphQLResponseError, PayloadVerificationError
  const.py           # Constants (INDENT, etc.)
test/
  test_components.py # pytest tests for GqlObject and Field
```

## Development Setup

```bash
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest test
```

## Linting & Formatting

- **Black** for formatting (version ~22.0): `black ./src` — CI checks `./src` only; `test/` is excluded
- **flake8** for linting: configured in `pyproject.toml` (max line length: 100)

## CI

GitHub Actions runs on push/PR to `main` across Ubuntu, Windows, macOS and Python 3.10–3.14. Steps: install deps → Black check → flake8 → pytest.

## Key Conventions

- Source lives under `src/` (PEP 517 layout); `pyproject.toml` uses `setuptools.packages.find` with `where = ["src"]`
- Tests use `pytest`; test path configured in `pyproject.toml` as `testpaths = ["test"]`
- Package installed in editable mode (`pip install -e .`) before running tests
- `__init__.py` uses wildcard re-exports from `components` and `operations`; flake8 F401 is suppressed for `__init__.py`
- Requires Python ≥ 3.10; runtime dependency is `requests~=2.33.1`
