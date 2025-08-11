# Turn Phase Guidelines

These rules apply to modules under `bang_py/turn_phases/`.

## Style
- Include a brief module-level docstring at the top of each file.
- Prefer built-in generics such as `list` and `dict` over `typing.List` and `typing.Dict`.
- Use `@override` from `typing` when overriding methods from parent classes.
- Keep lines at or below 100 characters.

## Testing
- Run `uv run pre-commit run --files <file> [<file> ...]` on modified files.
- Execute `uv run pytest` after changing this package.
