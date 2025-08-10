# QML Guidelines

## Style
- Wrap all user-facing text in `qsTr()` for translation.
- Provide input validators for user-editable fields whenever possible.
- Use four spaces for indentation and keep lines under 100 characters.

## Testing
- Run `uv run pre-commit run --files <file> [<file> ...]` after editing QML files.
- Execute `uv run pytest` to ensure tests pass.
