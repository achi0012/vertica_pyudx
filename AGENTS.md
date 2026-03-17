# Agent Working Doc for Vertica UDX

## Build / Lint / Test Commands

- **Build** – No compilation needed; Python scripts are interpreted by the Vertica engine.
- **Lint** – Run `ruff src tests` to get flake8+style checks.
- **Test** –
  ```bash
  # install dev deps
  pip install -r requirements-dev.txt
  # run full test suite
  pytest -q
  # run a single test case
  pytest tests/test_example.py::test_case -q
  ```

## Code Style Guidelines

- **Imports** – `import` statements grouped alphabetically, separated by a blank line between built‑ins, third‑party and local imports. Use `from module import Class` where appropriate.
- **Formatting** – 4‑space indentation, line length 88 characters. Enforce with `ruff --fix`. `black` style is used for automatic formatting.
- **Types** – Use `typing` annotations for all public functions and classes. Pydantic or `attrs` are not required.
- **Naming** – Functions and variables use `snake_case`. Classes use `PascalCase`. Constants use `UPPER_SNAKE_CASE`.
- **Error handling** – Raise explicit exceptions (`ValueError`, `RuntimeError`) with clear messages. Wrap external calls (e.g., `requests.post`) in try/except blocks and re‑raise as custom errors.
- **Docstrings** – One‑line summary followed by an empty line and a detailed description. Use Google‑style docstrings.
- **Tests** – Each UDX file has a corresponding `tests/test_<module>.py` with coverage ≥ 90 %. Tests use `pytest` and `pytest-mock` for monkeypatching.
- **File layout** – `src/` contains production code, `tests/` contains tests. `v_*` directories are not part of the `src` package; they remain at the repo root.

## Cursor / Copilot Rules

- No Cursor or Copilot instructions are present in this repository.
- All changes must follow the style guidelines specified above.

---

**Author**: openAI Assistant | **Date**: 2026‑03‑13