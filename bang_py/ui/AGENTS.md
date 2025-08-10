# UI Module Guidelines

## Style
- Require module docstrings and type hints.
- Use built-in generics and annotate overrides with `@override`.
- Keep lines ≤100 characters.

## Testing
- Run `uv run pre-commit run --files <file> [<file> ...]` on changed files.
- Execute `uv run pytest` after modifying this module.
