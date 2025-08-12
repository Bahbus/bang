
.RECIPEPREFIX := >
.PHONY: build-exe build-msi lint test

build-exe:
>mkdir -p build/bang
>echo "[Paths]\nPrefix=." > build/bang/qt.conf
>uv run pyinstaller scripts/bang.spec

build-msi: build-exe
>heat dir dist/bang --out bang.wixobj --cg BangFiles
>candle scripts/bang.wxs
>light bang.wixobj scripts/bang.wixobj -ext WixUIExtension -out dist/bang.msi
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
