# AI Mood Calendar

An AI-powered **Mood Logging and Mental Health Support** system that integrates:

- **Computer Vision (YOLOv8)** for detecting facial emotions via live webcam
- **Speech-to-Text (Google Speech Recognition)** for capturing voice notes
- **SQLite database** for storing per-user mood entries
- **Agent-based health assistant** powered by Google ADK (Gemini LLM) to analyze past moods and provide personalized mental health suggestions
- **Command-line tools** to fetch and manage mood logs



## Project Structure

    AI-Mood-Calendar/
    │
    ├── mood_logger_cv_stt.py # CLI tool to log mood entries with emotion detection + STT notes
    ├── fetch_moods.py # CLI tool to fetch and manage (delete/renumber) mood entries
    ├── agent.py # AI Agent (Gemini + ADK) that analyzes stored moods
    ├── prompt.py # Prompt template for the health agent
    ├── moods.db # SQLite database (auto-created on first run)
    ├── face_emotion_recognition.pt # YOLO model for facial emotion recognition (not included)
    ├── requirements.txt # Python dependencies
    └── README.md # Project documentation


## Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/ai-mood-calendar.git
    cd ai-mood-calendar
    ```

2.  **Create a virtual environment**
    ```bash
    python3 -m venv flask_calendar_env
    source flask_calendar_env/bin/activate  # Mac/Linux
    flask_calendar_env\Scripts\activate     # Windows
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```
    Important: Some packages (OpenCV + NumPy) require compatible versions.

    Recommended pins:
    ```bash
    pip install "numpy<2.0" opencv-python==4.10.0.84 speechrecognition ultralytics
    ```
4.  **Download YOLO model**

    Place your trained YOLOv8 model file (e.g., face_emotion_recognition.pt) in the project root.

    This model should be trained to detect facial emotions like Sad, Happy, Angry, Surprised.


## Usage

1.  **Log a new mood entry**

    Run the logger (uses camera + microphone):
    ```bash
    python mood_logger_cv_stt.py
    ```
    Flow:
    -   Enter ```user_id```
    -   Provide mood rating (1–10)
    -   Look into the camera → YOLO auto-detects your emotion
    -   Speak a note → converted to text
    -   Entry is stored in ```moods.db```
2.  **Fetch or manage past entries**

    Run:
    ```bash
    python fetch_moods.py
    ```
    Features:
    -   View last N entries for a user
    -   Delete entries
    -   Renumber remaining entries automatically
3.  **Run the AI Health Agent**

    The agent uses Google ADK (Agent Development Kit) with a Gemini LLM to analyze mood history.

    Start the agent:
    ```bash
    adk run agent:root_agent
    ```
    It will:
    -   Ask for your ```user_id``` and number of entries to analyze
    -   Fetch entries from ```moods.db```
    -   Suggest potential future actions to improve mental health


## Database Schema

The SQLite ```moods``` table:
|     Column    |   Type  |                 Description                  |
| ------------- | ------- | -------------------------------------------- |
|       id      | INTEGER |          Auto-increment primary key          |
|    user_id    |  TEXT   |               User identifier                |
| user_entry_id | INTEGER |    Sequential per-user entry number (1..N)   |
|      mood     | INTEGER |              Mood rating (1–10)              |
|     emotion   |  TEXT   | Emotion label (Sad, Happy, Angry, Surprised) |
|      note     |  TEXT   |     Optional note (from speech or manual)    |
|   created_at  |  TEXT   |              Timestamp of entry              |


## Example Workflow

```bash
$ python mood_logger_cv_stt.py
=== Mood Logger ===
Enter user ID: alice
Enter mood (1–10): 7
[Camera opens, detects "Happy"]
Recording note... Speak now.
>>> Press Enter when finished.
Captured Note: Had a great workout today!

Entry saved with emotion: Happy, note: Had a great workout today
```

```bash
$ python fetch_moods.py
=== Mood Fetcher ===
Enter user ID: alice
How many recent entries to fetch? 5

=== Last 1 entries for alice ===
(Entry #1) [Sep 11, 2025 01:30 PM] Mood: 7, Emotion: Happy, Note: Had a great workout today!
```

```bash
$ adk run agent:root_agent
AI Mental Health Support Assistant:
Hello! Please provide your user ID and the number of entries you’d like me to analyze.
```


## Requirements

-   Python 3.9+
-   Webcam + Microphone
-   Installed system dependencies for OpenCV & PyAudio:
    -   Mac/Linux:
        ```bash
        brew install portaudio ffmpeg
        ```
    -   Ubuntu:
        ```bash
        sudo apt-get install portaudio19-dev ffmpeg
        ```


## Future Improvements

-   Flask web interface with live camera + microphone capture
-   Chat-style frontend for interacting with the agent
-   Support for multiple users with authentication
-   Visualization of mood trends (graphs & charts)