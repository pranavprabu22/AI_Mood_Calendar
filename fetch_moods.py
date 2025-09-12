import sqlite3

DB_FILE = "moods.db"

def fetch_entries(user_id, limit):
    """Fetch the most recent `limit` entries for a user."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        SELECT user_entry_id, mood, emotion, note, created_at
        FROM moods
        WHERE user_id = ?
        ORDER BY user_entry_id DESC
        LIMIT ?
    """, (user_id, limit))
    rows = cur.fetchall()
    conn.close()
    return rows

def display_entries(entries, user_id):
    """Pretty print mood entries."""
    if not entries:
        print(f"No entries found for user '{user_id}'.")
    else:
        print(f"\n=== Last {len(entries)} entries for {user_id} ===")
        for entry_id, mood, emotion, note, created_at in entries:
            print(f"(Entry #{entry_id}) [{created_at}] "
                  f"Mood: {mood}, Emotion: {emotion}, Note: {note}")

def delete_entry(user_id, entry_id):
    """Delete an entry by per-user ID, then renumber remaining entries."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Delete the entry
    cur.execute("DELETE FROM moods WHERE user_id = ? AND user_entry_id = ?", (user_id, entry_id))
    deleted = cur.rowcount

    if deleted > 0:
        # Renumber remaining entries to be consecutive
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
    return deleted > 0

def main():
    print("=== Mood Fetcher ===")
    user_id = input("Enter user ID: ").strip()

    while True:
        try:
            limit = int(input("How many recent entries to fetch? ").strip())
            if limit > 0:
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid integer.")

    while True:
        entries = fetch_entries(user_id, limit)
        display_entries(entries, user_id)

        if not entries:
            break

        print("\nOptions:")
        print("1. Delete an entry")
        print("2. Refresh list")
        print("3. Change fetch limit")
        print("4. Quit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            try:
                entry_id = int(input("Enter the Entry # to delete: ").strip())
                if delete_entry(user_id, entry_id):
                    print(f"✅ Entry #{entry_id} deleted for user {user_id}.")
                else:
                    print(f"No entry #{entry_id} found for {user_id}.")
            except ValueError:
                print("Invalid ID. Must be a number.")
        elif choice == "2":
            continue  # loop will refetch automatically
        elif choice == "3":
            try:
                new_limit = int(input("Enter new fetch limit: ").strip())
                if new_limit > 0:
                    limit = new_limit
                else:
                    print("Fetch limit must be a positive number.")
            except ValueError:
                print("Invalid number.")
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please choose 1–4.")

if __name__ == "__main__":
    main()
