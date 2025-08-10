# Card Handler Guidelines

These rules apply to modules under `bang_py/card_handlers/`.

## Style
- Include a brief module-level docstring at the top of each file.
- Prefer built-in collection generics such as `list` and `dict` over
  `typing.List` and `typing.Dict`.
- Use the `@override` decorator when overriding methods from parent classes.
- Provide type hints for all public functions and keep lines at or below
  100 characters.

## Testing
- Run `uv run pre-commit run --files <file> [<file> ...]` on modified files.
- Execute `uv run pytest` after changing this package.
