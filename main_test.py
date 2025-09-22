#!/usr/bin/env python3
"""
Vereinfachte Test-Datei für Region-Selector Tests.
Alle Widget-Tests wurden entfernt - nur Region-Selector Tests bleiben.
"""


def show_menu():
    """Zeige das interaktive Menü."""
    print("\n" + "=" * 60)
    print("🎯 INTERAKTIVER REGION-SELECTOR TEST")
    print("=" * 60)
    print("Wähle einen Test aus:")
    print()
    print("1️⃣  Einfacher Selector (Simulation)")
    print("2️⃣  FUNKTIONIERENDER Selector - Kleine Region")
    print("3️⃣  FUNKTIONIERENDER Selector - Große Region")
    print("4️⃣  Qt-Selector - Ziehen und Auswählen")
    print("5️⃣  Abbruch-Test")
    print("6️⃣  Alle Tests nacheinander")
    print("7️⃣  Benutzerdefinierte Größe")
    print("8️⃣  Performance-Test")
    print("9️⃣  Screenshot-Test")
    print("🔟 Video-Aufnahme-Test")
    print("1️⃣1️⃣ Hilfe")
    print("0️⃣  Beenden")
    print()
    print("-" * 60)


def get_user_choice():
    """Hole die Benutzerauswahl."""
    while True:
        try:
            choice = input("🎯 Deine Wahl (0-11): ").strip()
            if choice in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"]:
                return choice
            else:
                print("❌ Ungültige Eingabe! Bitte wähle 0-11.")
        except KeyboardInterrupt:
            print("\n👋 Auf Wiedersehen!")
            return "0"


def test_simple_selector():
    """Test 1: Einfacher Selector."""
    print("\n📋 Test 1: Einfacher Selector")
    print("🔄 Simuliere Region-Auswahl...")
    try:
        from src.ui.region_selector import SimpleRegionSelector

        simple_selector = SimpleRegionSelector()
        result = simple_selector.select()
        print(f"✅ Simulierte Region: {result}")
        return True
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False


def test_mouse_centered_small():
    """Test 2: FUNKTIONIERENDER Selector - Kleine Region."""
    print("\n📋 Test 2: FUNKTIONIERENDER Selector - Kleine Region")
    print("🎯 Ziel: Wähle eine kleine Region (50x50) aus")
    print("\n📝 SCHRITT-FÜR-SCHRITT ANLEITUNG:")
    print("   1️⃣  Bewege die Maus zu der gewünschten Position")
    print("   2️⃣  Drehe das Mausrad NACH UNTEN um die Region zu verkleinern")
    print("   3️⃣  Wenn die Region klein genug ist:")
    print("       • Linksklick ODER")
    print("       • Enter-Taste ODER")
    print("       • Leertaste")
    print("   4️⃣  Zum Abbrechen: ESC oder Rechtsklick")
    print("\n⏳ Starte in 3 Sekunden...")

    import time

    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)

    try:
        from src.ui.simple_region_selector import SimpleRegionSelector

        selector = SimpleRegionSelector()
        result = selector.select()
        if result:
            print(f"✅ Kleine Region ausgewählt: {result}")
            if result.width <= 100 and result.height <= 100:
                print("   ✅ Größe ist klein wie gewünscht!")
            else:
                print("   ⚠️ Region ist größer als erwartet")
            return True
        else:
            print("❌ Keine Region ausgewählt oder abgebrochen")
            return False
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False


def test_mouse_centered_large():
    """Test 3: FUNKTIONIERENDER Selector - Große Region."""
    print("\n📋 Test 3: FUNKTIONIERENDER Selector - Große Region")
    print("🎯 Ziel: Wähle eine große Region (400x300) aus")
    print("📝 Anleitung: Mausrad nach oben für große Größe, dann Linksklick")
    print("⏳ Starte in 3 Sekunden...")

    import time

    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)

    try:
        from src.ui.simple_region_selector import SimpleRegionSelector

        selector = SimpleRegionSelector()
        result = selector.select()
        if result:
            print(f"✅ Große Region ausgewählt: {result}")
            if result.width >= 300 and result.height >= 200:
                print("   ✅ Größe ist groß wie gewünscht!")
            else:
                print("   ⚠️ Region ist kleiner als erwartet")
            return True
        else:
            print("❌ Keine Region ausgewählt oder abgebrochen")
            return False
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False


def test_qt_selector():
    """Test 4: Qt-Selector - Ziehen und Auswählen."""
    print("\n📋 Test 4: Qt-Selector - Ziehen und Auswählen")
    print("🎯 Ziel: Ziehe einen Bereich auf dem Bildschirm")
    print("📝 Anleitung: Klicke und ziehe um einen Bereich auszuwählen")
    print("⏳ Starte in 3 Sekunden...")

    import time

    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)

    try:
        from src.ui.region_selector import QtSelector

        qt_selector = QtSelector()
        result = qt_selector.select()
        if result:
            print(f"✅ Gezogene Region ausgewählt: {result}")
            print(f"   📏 Fläche: {result.width * result.height} Pixel")
            return True
        else:
            print("❌ Keine Region ausgewählt oder abgebrochen")
            return False
    except Exception as e:
        print(f"❌ Qt-Selector Fehler: {e}")
        print("   (PyQt6 möglicherweise nicht installiert)")
        return False


def test_cancel():
    """Test 5: Abbruch-Test."""
    print("\n📋 Test 5: Abbruch-Test")
    print("🎯 Ziel: Teste das Abbrechen der Auswahl")
    print("📝 Anleitung: Drücke ESC oder Rechtsklick zum Abbrechen")
    print("⏳ Starte in 3 Sekunden...")

    import time

    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)

    try:
        from src.ui.region_selector import MouseCenteredSelector

        mouse_selector = MouseCenteredSelector()
        result = mouse_selector.select()
        if result:
            print(f"✅ Region ausgewählt (nicht abgebrochen): {result}")
            return False  # Test fehlgeschlagen, da nicht abgebrochen
        else:
            print("✅ Erfolgreich abgebrochen!")
            return True
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False


def test_custom_size():
    """Test 7: Benutzerdefinierte Größe."""
    print("\n📋 Test 7: Benutzerdefinierte Größe")

    try:
        width = int(input("🎯 Gewünschte Breite (50-800): "))
        height = int(input("🎯 Gewünschte Höhe (50-600): "))

        if not (50 <= width <= 800 and 50 <= height <= 600):
            print("❌ Ungültige Größe! Verwende Standard-Größe.")
            width, height = 200, 150

        print(f"🎯 Ziel: Wähle eine {width}x{height} Region aus")
        print("📝 Anleitung: Verwende Mausrad um die Größe anzupassen, dann Linksklick")
        print("⏳ Starte in 3 Sekunden...")

        import time

        for i in range(3, 0, -1):
            print(f"   {i}...")
            time.sleep(1)

        from src.ui.region_selector import MouseCenteredSelector

        mouse_selector = MouseCenteredSelector()
        result = mouse_selector.select()
        if result:
            print(f"✅ Region ausgewählt: {result}")
            print(f"   🎯 Ziel: {width}x{height}")
            print(f"   📏 Tatsächlich: {result.width}x{result.height}")

            # Bewerte Genauigkeit
            width_diff = abs(result.width - width)
            height_diff = abs(result.height - height)
            if width_diff <= 20 and height_diff <= 20:
                print("   ✅ Sehr genau!")
            elif width_diff <= 50 and height_diff <= 50:
                print("   ✅ Gut!")
            else:
                print("   ⚠️ Könnte genauer sein")
            return True
        else:
            print("❌ Keine Region ausgewählt oder abgebrochen")
            return False
    except ValueError:
        print("❌ Ungültige Eingabe!")
        return False
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False


def test_performance():
    """Test 8: Performance-Test."""
    print("\n📋 Test 8: Performance-Test")
    print("🔄 Teste mehrere schnelle Auswahlen...")

    try:
        import time

        from src.ui.region_selector import SimpleRegionSelector

        start_time = time.time()
        results = []

        for i in range(10):
            selector = SimpleRegionSelector()
            result = selector.select()
            results.append(result)
            print(f"   Test {i+1}/10: {result}")

        end_time = time.time()
        duration = end_time - start_time

        print("✅ Performance-Test abgeschlossen!")
        print(f"   ⏱️ Dauer: {duration:.2f} Sekunden")
        print(f"   📊 Durchschnitt: {duration/10:.3f} Sekunden pro Test")
        print(f"   🎯 Erfolgsrate: {len([r for r in results if r])}/10")

        return True
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False


def test_screenshot():
    """Test 9: Screenshot-Test."""
    print("\n📋 Test 9: Screenshot-Test")
    print("📸 Mache einen Screenshot der ausgewählten Region")
    print("⏳ Starte in 3 Sekunden...")

    import time

    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)

    try:
        from src.ui.region_selector import ScreenCaptureSelector

        screenshot_selector = ScreenCaptureSelector("screenshot")
        result = screenshot_selector.select()
        if result:
            print("✅ Screenshot erfolgreich erstellt!")
            print("   📁 Gespeichert in: captures/")
            print(f"   📏 Region: {result.width}x{result.height}")
            return True
        else:
            print("❌ Screenshot fehlgeschlagen")
            return False
    except Exception as e:
        print(f"❌ Screenshot-Fehler: {e}")
        return False


def test_video_recording():
    """Test 10: Video-Aufnahme-Test."""
    print("\n📋 Test 10: Video-Aufnahme-Test")
    print("🎬 Nimm ein Video der ausgewählten Region auf")
    print("⏳ Starte in 3 Sekunden...")

    import time

    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)

    try:
        from src.ui.region_selector import ScreenCaptureSelector

        video_selector = ScreenCaptureSelector("video")
        result = video_selector.select()
        if result:
            print("✅ Video erfolgreich erstellt!")
            print("   📁 Gespeichert in: captures/")
            print(f"   📏 Region: {result.width}x{result.height}")
            return True
        else:
            print("❌ Video-Aufnahme fehlgeschlagen")
            return False
    except Exception as e:
        print(f"❌ Video-Aufnahme Fehler: {e}")
        return False


def show_help():
    """Zeige Hilfe."""
    print("\n📖 HILFE - Region-Selector Tests")
    print("=" * 50)
    print("🎯 Test-Typen:")
    print("   1️⃣  Simulation ohne UI")
    print("   2️⃣  Kleine Region (50x50)")
    print("   3️⃣  Große Region (400x300)")
    print("   4️⃣  Klassisches Ziehen")
    print("   5️⃣  Abbruch-Funktionalität")
    print("   6️⃣  Alle Tests nacheinander")
    print("   7️⃣  Eigene Größe wählen")
    print("   8️⃣  Performance messen")
    print("   9️⃣  Screenshot erstellen")
    print("   🔟 Video aufnehmen")
    print()
    print("🎮 Bedienung:")
    print("   • Maus bewegen: Region folgt der Maus")
    print("   • Mausrad hoch: Region vergrößern")
    print("   • Mausrad runter: Region verkleinern")
    print("   • Linksklick: Auswahl bestätigen")
    print("   • Enter-Taste: Auswahl bestätigen")
    print("   • Leertaste: Auswahl bestätigen")
    print("   • Rechtsklick: Abbrechen")
    print("   • ESC-Taste: Abbrechen")
    print("   • Ctrl+C: Video stoppen")
    print()
    print("💡 Tipps:")
    print("   • Teste verschiedene Größen")
    print("   • Achte auf Genauigkeit")
    print("   • Nutze Abbruch-Test für ESC-Funktion")
    print("   • Screenshots werden in captures/ gespeichert")
    print("   • Videos können mit Ctrl+C gestoppt werden")


def run_all_tests():
    """Führe alle Tests nacheinander aus."""
    print("\n🚀 Führe alle Tests aus...")

    tests = [
        ("Einfacher Selector", test_simple_selector),
        ("Kleine Region", test_mouse_centered_small),
        ("Große Region", test_mouse_centered_large),
        ("Qt-Selector", test_qt_selector),
        ("Abbruch-Test", test_cancel),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n🔄 Führe aus: {name}")
        try:
            result = test_func()
            results.append((name, result))
            if result:
                print(f"✅ {name}: Erfolgreich")
            else:
                print(f"❌ {name}: Fehlgeschlagen")
        except Exception as e:
            print(f"❌ {name}: Fehler - {e}")
            results.append((name, False))

        input("\n⏸️ Drücke Enter für nächsten Test...")

    # Zusammenfassung
    print("\n📊 ZUSAMMENFASSUNG:")
    print("-" * 40)
    successful = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅" if result else "❌"
        print(f"   {status} {name}")

    print(f"\n🎯 Erfolgsrate: {successful}/{total} ({successful/total*100:.1f}%)")


def test_region_selector():
    """Hauptfunktion für interaktive Tests."""
    try:
        while True:
            show_menu()
            choice = get_user_choice()

            if choice == "0":
                print("👋 Auf Wiedersehen!")
                break
            elif choice == "1":
                test_simple_selector()
            elif choice == "2":
                test_mouse_centered_small()
            elif choice == "3":
                test_mouse_centered_large()
            elif choice == "4":
                test_qt_selector()
            elif choice == "5":
                test_cancel()
            elif choice == "6":
                run_all_tests()
            elif choice == "7":
                test_custom_size()
            elif choice == "8":
                test_performance()
            elif choice == "9":
                test_screenshot()
            elif choice == "10":
                test_video_recording()
            elif choice == "11":
                show_help()

            if choice != "0":
                input("\n⏸️ Drücke Enter um fortzufahren...")

    except ImportError as e:
        print(f"❌ Import-Fehler: {e}")
    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_region_selector()
