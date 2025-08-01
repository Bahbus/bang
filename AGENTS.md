# Agent Guidelines

This repository contains a Python implementation of the Bang card game, a small
websocket server, and a Qt-based interface. To maintain consistency, follow
these rules when making changes.

## Development
- Use Python 3.13+.
- Target `websockets>=15.0.1`, `PySide6>=6.9.1` and `PyInstaller>=6.14.2`.
- After modifying code, run `pytest` from the repository root to ensure tests
  pass.
- Keep tests deterministic. If randomness is needed, seed the RNG inside the tests or offer hooks to bypass shuffling.
- Set `BANG_AUTO_CLOSE=1` when launching the UI in tests so it quits automatically.

## Style
- Follow standard PEP8 conventions and keep lines under 100 characters.
- Include type hints and docstrings for public classes and functions when
  appropriate.

## Pull Requests
- Summarize key changes and mention test results in the PR body.

The JPEG files `example-bang-menu-ui.jpg` and `example_bang_ui.jpg` located in
the repository root are provided only as reference screenshots. They should not
be loaded or otherwise used by the application code.
