import os
import sqlite3

print("Database path:", os.path.abspath("data/audio_database.db"))
print("Database exists:", os.path.exists("data/audio_database.db"))

if os.path.exists("data/audio_database.db"):
    conn = sqlite3.connect("data/audio_database.db")
    cursor = conn.cursor()

    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tables:", tables)

    # Check audio_recordings count
    try:
        cursor.execute("SELECT COUNT(*) FROM audio_recordings")
        count = cursor.fetchone()[0]
        print("Audio recordings count:", count)
    except Exception as e:
        print("Error checking audio_recordings:", e)

    # Check transcriptions count
    try:
        cursor.execute("SELECT COUNT(*) FROM transcriptions")
        count = cursor.fetchone()[0]
        print("Transcriptions count:", count)
    except Exception as e:
        print("Error checking transcriptions:", e)

    conn.close()
else:
    print("Database file not found!")
