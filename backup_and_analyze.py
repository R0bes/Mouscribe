import os
import shutil
import sqlite3
from datetime import datetime

# Check current database structure
print("=== CURRENT DATABASE STRUCTURE ===")
conn = sqlite3.connect("data/audio_database.db")
cursor = conn.cursor()

print("\nAUDIO_RECORDINGS table structure:")
cursor.execute("PRAGMA table_info(audio_recordings)")
for row in cursor.fetchall():
    print(f"  {row[1]} ({row[2]})")

print("\nTRANSCRIPTIONS table structure:")
cursor.execute("PRAGMA table_info(transcriptions)")
for row in cursor.fetchall():
    print(f"  {row[1]} ({row[2]})")

# Count records
cursor.execute("SELECT COUNT(*) FROM audio_recordings")
audio_count = cursor.fetchone()[0]
print(f"\nAudio recordings: {audio_count}")

cursor.execute("SELECT COUNT(*) FROM transcriptions")
transcription_count = cursor.fetchone()[0]
print(f"Transcriptions: {transcription_count}")

conn.close()

# Create backup
print("\n=== CREATING BACKUP ===")
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = f"data/backup_{timestamp}"
os.makedirs(backup_dir, exist_ok=True)

# Backup database
shutil.copy2("data/audio_database.db", f"{backup_dir}/audio_database.db")
print(f"Database backed up to: {backup_dir}/audio_database.db")

# Backup audio files directory
if os.path.exists("data/audio"):
    shutil.copytree("data/audio", f"{backup_dir}/audio")
    print(f"Audio files backed up to: {backup_dir}/audio/")

print(f"\nBackup completed in: {backup_dir}")
