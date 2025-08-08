# Card Handler Guidelines

These rules apply to modules under `bang_py/card_handlers/`.

- Include a brief module-level docstring at the top of each file.
- Prefer built-in generics such as `list` and `dict` over `typing.List` and `typing.Dict`.
- Use `@override` from `typing` when overriding methods from parent classes.
