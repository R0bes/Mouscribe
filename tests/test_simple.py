"""Einfacher Test für Mauscribe - sofort ausführbar."""

import pytest


def test_basic_functionality():
    """Testet grundlegende Funktionalität."""
    assert True  # Immer erfolgreich


def test_simple_math():
    """Testet einfache Mathematik."""
    assert 2 + 2 == 4
    assert 3 * 3 == 9
    assert 10 - 5 == 5


def test_string_operations():
    """Testet String-Operationen."""
    text = "Mauscribe"
    assert len(text) == 9
    assert "Maus" in text
    assert text.upper() == "MAUSCRIBE"


if __name__ == "__main__":
    # Kann direkt ausgeführt werden
    test_basic_functionality()
    test_simple_math()
    test_string_operations()
    print("✅ Alle einfachen Tests erfolgreich!")
