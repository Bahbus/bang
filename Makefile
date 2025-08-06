.RECIPEPREFIX := >
.PHONY: build-exe lint test

build-exe:
>mkdir -p build/bang
>echo "[Paths]\nPrefix=." > build/bang/qt.conf
>pyinstaller bang.spec

lint:
>@pre-commit run --files $(FILES)

test:
>@pytest
