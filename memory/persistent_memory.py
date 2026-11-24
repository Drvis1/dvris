import sqlite3
import json
from typing import List, Dict
from langchain_core.messages import BaseMessage, messages_from_dict, messages_to_dict
from config.settings import settings

class PersistentConversationMemory:
    """
    持久化对话记忆，sqlite存储，支持多session_id隔离会话，退出不丢失
    """
    def __init__(self):
        self.conn = sqlite3.connect(settings.MEMORY_DB_PATH, check_same_thread=False)
        self._init_table()

    def _init_table(self):
        cur = self.conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS conversation_memory (
            session_id TEXT PRIMARY KEY,
            message_json TEXT
        )
        """)
        self.conn.commit()

    def load_messages(self, session_id: str) -> List[BaseMessage]:
        cur = self.conn.cursor()
        row = cur.execute("SELECT message_json FROM conversation_memory WHERE session_id=?", (session_id,)).fetchone()
        if not row:
            return []
        msg_dict = json.loads(row[0])
        return messages_from_dict(msg_dict)

    def save_messages(self, session_id: str, messages: List[BaseMessage]):
        msg_json = json.dumps(messages_to_dict(messages), ensure_ascii=False)
        cur = self.conn.cursor()
        cur.execute("""
        INSERT OR REPLACE INTO conversation_memory(session_id, message_json)
        VALUES (?, ?)
        """, (session_id, msg_json))
        self.conn.commit()

    def clear_session(self, session_id: str):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM conversation_memory WHERE session_id=?", (session_id,))
        self.conn.commit()

memory_store = PersistentConversationMemory()