# Python justfile

# Run all gates in sequence -- this is what the pre-commit hook calls
check: format-check lint typecheck test

# Format in place with ruff
format:
    uv run ruff format .
    uv run ruff check --fix .

# Check formatting without modifying files (for CI gate)
format-check:
    uv run ruff format --check .

# Lint; no auto-fix (gate mode -- errors must be visible)
lint:
    uv run ruff check .

# Type check the full project
typecheck:
    uv run pyright

# Run tests
test:
    uv run pytest

# Run tests with coverage
test-coverage:
    uv run pytest --cov=src --cov-report=term-missing

# Sync dependencies from lockfile (run after pulling changes)
sync:
    uv sync

# Bootstrap: set up environment and hooks
bootstrap:
    uv sync
    uv run pre-commit install
    @echo "Bootstrap complete. Run 'just check' to verify."

# Update pre-commit hooks to latest versions
hooks-update:
    uv run pre-commit autoupdate
