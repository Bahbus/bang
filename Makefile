.RECIPEPREFIX := >
.PHONY: build-exe

build-exe:
>mkdir -p build/bang
>echo "[Paths]\nPrefix=." > build/bang/qt.conf
>pyinstaller bang.spec
