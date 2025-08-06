# Test Guidelines
- Set the event deck explicitly or call `random.seed()` in tests to avoid flaky behavior.
- The following tests are marked `@pytest.mark.slow` and skipped by default:
  - `test_bang_executable` verifies the PyInstaller build. Run it with
    `pytest -m slow tests/test_bang_executable.py` when PyInstaller is available.
  - `test_full_game_simulation` plays automated games for multiple player counts.
    Execute it via `pytest -m slow tests/test_full_game_simulation.py`.
  - `test_network_integration` exercises websocket server/client flow and SSL. Run it
    with `pytest -m slow tests/test_network_integration.py`.
  - `test_network_messages` checks server handling of malformed or oversized messages.
    Execute it with `pytest -m slow tests/test_network_messages.py`.
  - `test_server_task_cleanup` ensures server tasks shut down cleanly after a disconnect.
    Run it with `pytest -m slow tests/test_server_task_cleanup.py`.
