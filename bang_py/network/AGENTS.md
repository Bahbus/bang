# Agent Guidelines

## Style
- Use `asyncio` APIs with `TaskGroup` for managing concurrency when suitable.
- Decorate methods that override base class implementations with `@override`.
- Keep lines at or below 100 characters and write docstrings for public functions.

## Testing
- Run `uv run pre-commit run --files <file> [<file> ...]` on changes.
- Execute `uv run pytest` after modifying this package.
