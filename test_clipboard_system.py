#!/usr/bin/env python3
"""
Test-Skript für das Mauscribe Clipboard-System
Validiert pyperclip und pyautogui Funktionalität
"""

import time

import pyautogui
import pyperclip


def test_pyperclip():
    """Test pyperclip functionality."""
    print("🧪 Teste pyperclip...")

    try:
        # Test-Text
        test_text = f"Mauscribe Clipboard-Test {int(time.time())}"
        print(f"📝 Test-Text: '{test_text}'")

        # Kopiere Text
        pyperclip.copy(test_text)
        print("📋 Text kopiert")

        # Lese Text zurück
        retrieved_text = pyperclip.paste()
        print(f"📖 Gelesener Text: '{retrieved_text}'")

        if retrieved_text == test_text:
            print("✅ pyperclip funktioniert korrekt!")
            return True
        else:
            print(f"❌ pyperclip Test fehlgeschlagen: '{test_text}' != '{retrieved_text}'")
            return False

    except Exception as e:
        print(f"❌ pyperclip Test fehlgeschlagen: {e}")
        return False


def test_pyautogui():
    """Test pyautogui functionality."""
    print("\n🧪 Teste pyautogui...")

    try:
        # Test-Text
        test_text = "pyautogui Test"
        print(f"📝 Test-Text: '{test_text}'")

        # Kurze Pause
        print("⏳ 3 Sekunden Pause - bewege Cursor in ein Textfeld...")
        time.sleep(3)

        # Text eingeben
        pyautogui.write(test_text)
        print("⌨️  Text eingegeben")

        print("✅ pyautogui Test abgeschlossen!")
        return True

    except Exception as e:
        print(f"❌ pyautogui Test fehlgeschlagen: {e}")
        return False


def test_clipboard_integration():
    """Test complete clipboard integration."""
    print("\n🧪 Teste komplette Clipboard-Integration...")

    try:
        # Test-Text
        test_text = f"Integration Test {int(time.time())}"
        print(f"📝 Test-Text: '{test_text}'")

        # Kopiere in Clipboard
        pyperclip.copy(test_text)
        print("📋 Text in Clipboard kopiert")

        # Kurze Pause
        print("⏳ 3 Sekunden Pause - bewege Cursor in ein Textfeld...")
        time.sleep(3)

        # Lese aus Clipboard und füge ein
        clipboard_text = pyperclip.paste()
        if clipboard_text == test_text:
            print("✅ Clipboard-Text korrekt gelesen")

            # Text einfügen
            pyautogui.write(clipboard_text)
            print("⌨️  Text eingefügt")

            print("✅ Clipboard-Integration funktioniert!")
            return True
        else:
            print(f"❌ Clipboard-Text stimmt nicht überein: '{test_text}' != '{clipboard_text}'")
            return False

    except Exception as e:
        print(f"❌ Clipboard-Integration Test fehlgeschlagen: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 Mauscribe Clipboard-System Test")
    print("=" * 40)

    # Test pyperclip
    pyperclip_ok = test_pyperclip()

    # Test pyautogui
    pyautogui_ok = test_pyautogui()

    # Test Integration
    integration_ok = test_clipboard_integration()

    # Zusammenfassung
    print("\n" + "=" * 40)
    print("📊 TEST-ZUSAMMENFASSUNG:")
    print(f"pyperclip: {'✅' if pyperclip_ok else '❌'}")
    print(f"pyautogui: {'✅' if pyautogui_ok else '❌'}")
    print(f"Integration: {'✅' if integration_ok else '❌'}")

    if all([pyperclip_ok, pyautogui_ok, integration_ok]):
        print("\n🎉 Alle Tests erfolgreich! Clipboard-System funktioniert.")
    else:
        print("\n⚠️  Einige Tests fehlgeschlagen. Überprüfe die Installation.")

    print("\n💡 Tipp: Stelle sicher, dass der Cursor in einem Textfeld steht, bevor pyautogui Tests laufen.")


if __name__ == "__main__":
    main()
