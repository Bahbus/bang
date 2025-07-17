.PHONY: build-exe

build-exe:
	pyinstaller --onefile bang.spec
