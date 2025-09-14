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


## Process

The development of the AI Mood Calendar followed a multi-stage, iterative design process that combined emotion recognition, natural language processing, and database management:

1.  **Problem Framing**
    -   The goal was to create a system that could log and analyze moods using both facial expressions and voice input.
    -   Initial prototypes considered purely text-based journaling but were expanded to multimodal input (vision + speech) to reduce friction and increase expressiveness.
2.  **Model Selection for Emotion Recognition**
    -   Early testing with pre-trained CNN emotion classifiers revealed performance limitations in uncontrolled lighting conditions.
    -   YOLOv8 was chosen for its strong real-time detection capabilities, scalability, and support for fine-tuning on emotion-specific datasets.
    -   This decision reflected the need to balance inference accuracy with latency for live webcam use.
3.  **Speech-to-Text Integration**
    -   Google Speech Recognition was integrated for voice-based notes.
    -   Alternatives such as Whisper were considered but set aside initially to keep the system lightweight and dependency-friendly.
    -   This required trial-and-error with microphone handling and error recovery for cases where speech was unclear or background noise interfered.
4.  **Database Schema Design**
    -   The first prototype stored entries in JSON, but scalability and query limitations led to adopting SQLite.
    -   The schema was carefully designed to include per-user sequential IDs, timestamps, and multimodal data (ratings, emotions, notes).
    -   This structure supported both retrieval efficiency and extensibility for analytics.
5.  **Agent Integration**
    -   The health assistant was developed using Google ADK and Gemini LLM.
    -   Early iterations experimented with simple prompt engineering, but eventually evolved into a modular template system for more consistent guidance.
    -   Handling variable-length histories and diverse user input required refining how data was pre-processed and summarized before being sent to the LLM.
6.  **Command-Line Tools and Usability**
    -   Initial logging scripts were functional but cumbersome. Iterative improvements added structured prompts, error handling, and sequential ID management.
    -   Separate CLI tools for logging, fetching, and management were introduced for modularity and ease of testing.
7.  **Testing and Iteration**
    -   Trial runs highlighted challenges in synchronizing multimodal input (camera + microphone).
    -   Fail-safes (e.g., skipping speech-to-text if no input detected) and defaults (e.g., “Neutral” emotion if face not detected) were introduced to improve reliability.


## Key Learnings

The project provided insights into the integration of multimodal data collection, storage, and analysis within a health-focused application.

1.  **Multimodal System Design**
    -   Combining computer vision and speech recognition required careful synchronization and robust error handling.
    -   This highlighted principles of modularity and fault tolerance in system integration.
2.  **Database-Backed Logging for Longitudinal Analysis**
    -   Using SQLite emphasized the importance of structured, queryable storage for time-series data.
    -   The schema design reinforced how thoughtful data modeling enables more meaningful downstream analysis.
3.  **Real-Time Emotion Recognition Tradeoffs**
    -   The choice of YOLOv8 reflected the recurring tradeoff in real-time systems between inference speed and classification precision.
    -   It demonstrated how engineering constraints often guide model selection as much as accuracy metrics do.
4.  **LLM Integration for Personalized Feedback**
    -   Incorporating Gemini via ADK illustrated the potential of agents to contextualize data and provide tailored suggestions.
    -   It also raised challenges in ensuring reliability, interpretability, and alignment with user expectations—core issues in applied AI.
5.  **Human-Centered and Ethical Considerations**
    -   Handling sensitive emotional and mental health data brought attention to privacy, consent, and transparency.
    -   This reinforced the responsibility of designing systems that safeguard user data while delivering utility.
6.  **Scalability and Extensibility**
    -   The modular design—separating logging, data management, and agent analysis—facilitates future expansions (e.g., visualization dashboards, authentication, multi-user environments).
    -   This reflects the importance of designing for adaptability in evolving user needs.

Overall, the AI Mood Calendar demonstrated how multimodal input, structured storage, and agent-based reasoning can be combined to support mental health applications, while applying foundational CS principles of modularity, robustness, and ethical system design.


## Future Improvements

-   Flask web interface with live camera + microphone capture
-   Chat-style frontend for interacting with the agent
-   Support for multiple users with authentication
-   Visualization of mood trends (graphs & charts)

**Made by Pranav Prabu**
