
.RECIPEPREFIX := >
.PHONY: build-exe build-msi lint test

build-exe:
>mkdir -p build/bang
>echo "[Paths]\nPrefix=." > build/bang/qt.conf
>uv run pyinstaller scripts/bang.spec

build-msi: build-exe
>heat dir dist/bang -out bang-files.wxs -cg BangFiles -dr INSTALLDIR -gg -srd -sw5150
>candle bang-files.wxs -o bang-files.wixobj
>candle scripts/bang.wxs -o bang-script.wixobj
>light bang-files.wixobj bang-script.wixobj -ext WixUIExtension -out dist/bang.msi
>if [ -n "$$PFX_PATH" ] && [ -n "$$PFX_PASS" ]; then \
>  signtool sign /fd SHA256 /f "$$PFX_PATH" /p "$$PFX_PASS" dist/bang.msi; \
>else \
>  echo "Skipping signing"; \
>fi
>uv run python scripts/generate_checksums.py

lint:
>@uv run pre-commit run --files $(if $(FILES),$(FILES),$(shell git ls-files '*.py'))

test:
>@uv run pytest
