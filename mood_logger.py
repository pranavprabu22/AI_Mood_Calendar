import sqlite3
from datetime import datetime

DB_FILE = "moods.db"

def init_db():
    """Initialize the database with per-user entry IDs."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS moods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,      -- global unique id
            user_id TEXT NOT NULL,
            user_entry_id INTEGER NOT NULL,            -- per-user numbering
            mood INTEGER CHECK(mood >= 1 AND mood <= 10),
            emotion TEXT,
            note TEXT,
            created_at TEXT NOT NULL,
            UNIQUE(user_id, user_entry_id)             -- ensure per-user uniqueness
        )
    """)
    conn.commit()
    conn.close()

def renumber_entries(user_id):
    """Ensure per-user entries are numbered 1..N consecutively."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        SELECT id FROM moods
        WHERE user_id = ?
        ORDER BY user_entry_id
    """, (user_id,))
    rows = cur.fetchall()

    for new_id, (row_id,) in enumerate(rows, start=1):
        cur.execute("UPDATE moods SET user_entry_id = ? WHERE id = ?", (new_id, row_id))

    conn.commit()
    conn.close()

def add_entry(user_id, mood, emotion, note):
    """Insert a new mood entry with per-user ID tracking, renumbered cleanly."""
    # First, renumber existing entries for this user
    renumber_entries(user_id)

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Find the next entry number (count existing + 1)
    cur.execute("SELECT COUNT(*) FROM moods WHERE user_id = ?", (user_id,))
    next_id = cur.fetchone()[0] + 1

    created_at = datetime.now().strftime("%b %d, %Y %I:%M %p")  # readable timestamp

    cur.execute("""
        INSERT INTO moods (user_id, user_entry_id, mood, emotion, note, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, next_id, mood, emotion, note, created_at))
    conn.commit()
    conn.close()

def list_entries():
    """Retrieve and print entries ordered by user_id and per-user ID."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, user_entry_id, mood, emotion, note, created_at
        FROM moods
        ORDER BY user_id, user_entry_id
    """)
    rows = cur.fetchall()
    conn.close()
    
    if not rows:
        print("No entries found.")
    else:
        for row in rows:
            user_id, entry_id, mood, emotion, note, created_at = row
            print(f"(Entry #{entry_id} for {user_id}) [{created_at}] "
                  f"Mood: {mood}, Emotion: {emotion}, Note: {note}")

def main():
    init_db()
    print("=== Mood Logger ===")
    user_id = input("Enter user ID: ").strip()
    
    while True:
        # Mood input
        while True:
            try:
                mood = int(input("Enter mood (1–10): ").strip())
                if 1 <= mood <= 10:
                    break
                else:
                    print("Mood must be between 1 and 10.")
            except ValueError:
                print("Please enter a valid number.")

        # Emotion input
        emotion = input("Enter emotion (max 10 chars): ").strip()[:10]
        note = input("Enter note/description: ").strip()

        add_entry(user_id, mood, emotion, note)
        print("Entry saved.\n")

        # Ask if the user wants to continue
        cont = input("Add another entry? (y/n): ").strip().lower()
        if cont != "y":
            break

    print("\n=== All Entries (by user & time) ===")
    list_entries()

if __name__ == "__main__":
    main()
