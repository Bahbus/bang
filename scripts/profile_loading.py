"""Benchmark asset loading to verify cache effectiveness."""

from __future__ import annotations

from time import perf_counter

from bang_py.ui.components import card_images
from PySide6 import QtWidgets


def main() -> None:
    """Profile card composition and sound loading with and without caches."""
    app = QtWidgets.QApplication([])
    loader = card_images.get_loader()

    start = perf_counter()
    loader.compose_card("blue", 1, "Spades", name="bang")
    first_compose = perf_counter() - start

    start = perf_counter()
    loader.compose_card("blue", 1, "Spades", name="bang")
    second_compose = perf_counter() - start

    print(f"First compose: {first_compose:.6f}s")
    print(f"Second compose (cached): {second_compose:.6f}s")

    start = perf_counter()
    card_images.load_sound("bang")
    first_sound = perf_counter() - start

    start = perf_counter()
    card_images.load_sound("bang")
    second_sound = perf_counter() - start

    print(f"First sound load: {first_sound:.6f}s")
    print(f"Second sound load (cached): {second_sound:.6f}s")
    app.quit()


if __name__ == "__main__":
    main()
