.RECIPEPREFIX := >
.PHONY: build-exe lint test

build-exe:
>mkdir -p build/bang
>echo "[Paths]\nPrefix=." > build/bang/qt.conf
>pyinstaller scripts/bang.spec

lint:
>@pre-commit run --files $(if $(FILES),$(FILES),$(shell git ls-files '*.py'))

test:
>@pytest
