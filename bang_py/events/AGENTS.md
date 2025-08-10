# Agent Guidelines for events

## Style
- All modules in this directory must include a module-level docstring.
- Use built-in collection generics such as `list[int]` and `dict[str, str]`
  rather than `typing.List` or `typing.Dict`.
- Apply the `@override` decorator from `typing` when overriding methods.

## Testing
- Run `uv run pre-commit run --files <file> [<file> ...]` after editing.
- Execute `uv run pytest` to ensure event tests pass.
