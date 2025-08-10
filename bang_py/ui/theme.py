"""Utility functions for styling the Qt interface."""

from __future__ import annotations

import os

DEFAULT_THEME = "light"


def get_current_theme() -> str:
    """Return the theme specified by ``BANG_THEME`` or the default."""
    return os.getenv("BANG_THEME", DEFAULT_THEME)


def get_stylesheet(theme: str) -> str:
    """Return a Qt stylesheet string for the requested theme."""
    if theme == "dark":
        return """
            QWidget {
                background-color: #2b2b2b;
                color: #dddddd;
                font-family: "Segoe UI";
                font-size: 16px;
            }
            QPushButton {
                background-color: #444444;
                border: 2px solid #888888;
                min-width: 80px;
                max-width: 150px;
            }
            QLineEdit {
                background-color: #3c3c3c;
                color: #ffffff;
            }
            """
    return """
        QWidget {
            background-color: #deb887;
            color: #000000;
            font-family: "Segoe UI";
            font-size: 16px;
        }
        QPushButton {
            background-color: #f4a460;
            border: 2px solid #8b4513;
            min-width: 80px;
            max-width: 150px;
        }
        QLineEdit {
            background-color: #fff8dc;
            color: #000000;
        }
        """
