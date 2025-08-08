# Character Guidelines

These rules apply to files under `bang_py/characters/`.

## Docstrings
- Each character module must start with a brief docstring describing the character's ability.
- The docstring must reference the expansion where the character appears. Note "Core Set" for
  base game characters.

## Type hints
- Include `from __future__ import annotations` at the top of each module.
- Provide type hints for all function arguments and return types.

## Expansion references
- If a character belongs to an expansion, mention it in the module docstring, e.g., "Dodge City
  expansion".
- When multiple expansions apply, list each one.

Always consult this file before adding or modifying character classes.
