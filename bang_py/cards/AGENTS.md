# Card Module Guidelines

To keep card implementations consistent, follow these rules for files in this
folder.

- Start every file with a short module-level docstring.
- In docstrings, mention the expansion a card belongs to, when applicable.
- Prefer built-in generics such as `list` and `dict`, and use the `| None` syntax
  for optional types.
- Use `@override` when overriding methods from parent classes.
