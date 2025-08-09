.RECIPEPREFIX := >
.PHONY: build-exe lint test

build-exe:
>mkdir -p build/bang
>echo "[Paths]\nPrefix=." > build/bang/qt.conf
>uv run pyinstaller scripts/bang.spec

lint:
>@uv run pre-commit run --files $(if $(FILES),$(FILES),$(shell git ls-files '*.py'))

test:
>@uv run pytest
