import sqlite3
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import FunctionTool
import logging
from typing import Optional
from . import prompt

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)


MODEL = "gemini-2.0-flash"
DB_FILE = "moods.db"
# APP_NAME = "mood_app"

# USER_ID = "user123"  # default, can be changed interactively
# SESSION_ID = "session123"


def fetch_last_entries(user_id: str, limit: Optional[int] = None) -> dict:
    """
    Fetch the most recent mood entries for a user from the database.
    Returns both structured data (list of dicts) and a formatted string.
    """
    user_id = user_id.strip()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, mood, emotion, note, created_at
        FROM moods
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (user_id, limit))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return {
            "status": "error",
            "error_message": f"No entries found for user {user_id}."
        }

    # Build structured list of entries
    entries_list = [
        {
            "user_id": row[0],
            "mood": row[1],
            "emotion": row[2] if row[2] else None,
            "note": row[3] if row[3] else None,
            "created_at": row[4]
        }
        for row in rows[::-1]  # reverse so oldest → newest
    ]

    # Optional: formatted string for display
    formatted = "\n".join(
        f"[{e['created_at']}] Mood {e['mood']} | Emotion {e['emotion']} | Note: {e['note'] or 'No note'}"
        for e in entries_list
    )

    return {
        "status": "success",
        "entries": entries_list,
        "formatted": formatted
    }

# def fetch_last_entries(user_id: str, limit: int = 7):
#     conn = sqlite3.connect(DB_FILE)
#     cursor = conn.cursor()
#     cursor.execute("""
#         SELECT user_entry_id, mood, emotion, note, created_at
#         FROM moods
#         WHERE user_id = ?
#         ORDER BY created_at DESC
#         LIMIT ?
#     """, (user_id, limit))
#     rows = cursor.fetchall()
#     conn.close()
#     return rows[::-1]  # oldest → newest

# # def format_entries(entries):
#     return "\n".join(
#         f"[{e[4]}] Entry {e[0]} | Mood {e[1]} {e[2] or ''} | Note: {e[3] or 'No note'}"
#         for e in entries
#     )

# # Step 1: Create a ThinkingConfig
# thinking_config = ThinkingConfig(
#     include_thoughts=True,
#     thinking_budget=512
# )

# # Step 2: Instantiate BuiltInPlanner
# planner = BuiltInPlanner(thinking_config=thinking_config)

entries_tool = FunctionTool(func=fetch_last_entries)

# Step 3: Wrap the planner in an LlmAgent
root_agent = LlmAgent(
    model=MODEL,
    name="mood_analysis_agent",
    instruction=prompt.HEALTH_AGENT_PROMPT,
    output_key="health_advice",
    tools=[entries_tool]
)

# # Session and Runner
# session_service = InMemorySessionService()
# session = asyncio.run(session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID))
# runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)

# def call_agent(query):
#     content = Content(role="user", parts=[Part(text=query)])
#     events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)
    
#     for event in events:
#         if event.is_final_response() and event.content:
#             return event.content.parts[0].text.strip()
#     return "No response from agent."

