import sqlite3
from datetime import datetime
import cv2
from ultralytics import YOLO

DB_FILE = "moods.db"

# Load YOLO model once
MODEL_FILE = "face_emotion_recognition.pt"
model = YOLO(MODEL_FILE)

# Expected emotion labels from training
VALID_EMOTIONS = ["Sad", "Happy", "Angry", "Surprised"]

def init_db():
    """Initialize the database with per-user entry IDs."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS moods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            user_entry_id INTEGER NOT NULL,
            mood INTEGER CHECK(mood >= 1 AND mood <= 10),
            emotion TEXT,
            note TEXT,
            created_at TEXT NOT NULL,
            UNIQUE(user_id, user_entry_id)
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

def capture_emotion():
    """Capture emotion using YOLO model from webcam."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera not available. Falling back to manual entry.")
        return None

    print("Starting camera... Look at the camera. Press 'q' to lock emotion.")
    detected_emotion = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            break

        # Run YOLO model
        results = model(frame, verbose=False)

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                emotion = model.names[cls_id]
                if emotion in VALID_EMOTIONS:
                    detected_emotion = emotion
                    # Draw box & label
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, emotion, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Emotion Capture (press q to lock)", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    return detected_emotion

def add_entry(user_id, mood, emotion, note):
    """Insert a new mood entry with per-user ID tracking, renumbered cleanly."""
    renumber_entries(user_id)

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM moods WHERE user_id = ?", (user_id,))
    next_id = cur.fetchone()[0] + 1

    created_at = datetime.now().strftime("%b %d, %Y %I:%M %p")

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

        # Emotion input via YOLO
        emotion = capture_emotion()
        if not emotion:
            emotion = input("Could not auto-detect. Enter emotion (Sad/Happy/Angry/Surprised): ").strip().lower()

        note = input("Enter note/description: ").strip()

        add_entry(user_id, mood, emotion, note)
        print(f"Entry saved with emotion: {emotion}\n")

        cont = input("Add another entry? (y/n): ").strip().lower()
        if cont != "y":
            break

    print("\n=== All Entries (by user & time) ===")
    list_entries()

if __name__ == "__main__":
    main()
