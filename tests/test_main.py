"""Basic test to verify the test runner is wired."""

import importlib


def test_main_imports() -> None:
    """Verify that main module can be imported."""
    assert importlib.import_module("main") is not None
