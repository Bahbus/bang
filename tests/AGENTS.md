# Test Guidelines
- Set the event deck explicitly or call `random.seed()` in tests to avoid flaky behavior.
- The `test_bang_executable` test is marked `@pytest.mark.slow` and skipped by default.
  Run it manually with `pytest -m slow` when PyInstaller is available.
