# Character Guidelines

These rules apply to files under `bang_py/characters/`.

## Style
- Start each module with a docstring describing the character's ability and
  noting the expansion (use "Core Set" for base-game characters).
- Include `from __future__ import annotations` at the top of each module.
- Provide type hints for all function arguments and return values.
- Prefer built-in collection generics such as `list` and `dict` over
  `typing.List` and `typing.Dict`.
- Use the `@override` decorator when overriding methods from parent classes.
- Keep lines at or below 100 characters.

## Testing
- Run `uv run pre-commit run --files <file> [<file> ...]` on modified files.
- Execute `uv run pytest` after changing this package.

Always consult this file before adding or modifying character classes.
