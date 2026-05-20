from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from config import MAX_CHAT_HISTORY
from agent import database


class MemoryManager:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self._short_term: list[BaseMessage] = []
        self._load_from_db()

    def _load_from_db(self):
        records = database.load_conversation(self.project_id, MAX_CHAT_HISTORY * 2)
        for r in records:
            role = r["role"]
            content = r["content"]
            if role == "human":
                self._short_term.append(HumanMessage(content=content))
            elif role == "ai":
                self._short_term.append(AIMessage(content=content))

    @property
    def short_term(self) -> list[BaseMessage]:
        return self._short_term

    def add_message(self, role: str, content: str):
        database.save_conversation_message(self.project_id, role, content)

        if role == "human":
            self._short_term.append(HumanMessage(content=content))
        else:
            self._short_term.append(AIMessage(content=content))

        while len(self._short_term) > MAX_CHAT_HISTORY * 2:
            self._short_term.pop(0)

    def get_chat_history(self) -> list[BaseMessage]:
        return list(self._short_term)

    def get_context_for_prompt(self) -> str:
        return ""

    def clear(self):
        self._short_term.clear()
        database.clear_conversation(self.project_id)
