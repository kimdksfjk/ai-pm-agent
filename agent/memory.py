from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_classic.memory import ConversationSummaryBufferMemory
from langchain_openai import ChatOpenAI
from config import LLM_MODEL, LLM_API_KEY, LLM_BASE_URL, MAX_CHAT_HISTORY, SUMMARY_THRESHOLD


class MemoryManager:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self._short_term: list[BaseMessage] = []
        self._summary_memory: ConversationSummaryBufferMemory | None = None
        self._use_llm = bool(LLM_API_KEY)

    @property
    def short_term(self) -> list[BaseMessage]:
        return self._short_term

    def add_message(self, role: str, content: str):
        if role == "human":
            self._short_term.append(HumanMessage(content=content))
        else:
            self._short_term.append(AIMessage(content=content))

        if len(self._short_term) > MAX_CHAT_HISTORY:
            self._short_term = self._short_term[-MAX_CHAT_HISTORY:]

    def get_chat_history(self) -> list[BaseMessage]:
        return list(self._short_term)

    def get_summary(self) -> str:
        if self._summary_memory and self._summary_memory.buffer:
            return self._summary_memory.buffer
        return ""

    def maybe_summarize(self) -> str | None:
        if not self._use_llm or len(self._short_term) < SUMMARY_THRESHOLD:
            return None

        try:
            llm = ChatOpenAI(
                model=LLM_MODEL,
                api_key=LLM_API_KEY,
                base_url=LLM_BASE_URL,
                temperature=0,
            )
            self._summary_memory = ConversationSummaryBufferMemory(
                llm=llm,
                max_token_limit=2000,
                return_messages=True,
            )
            for msg in self._short_term:
                if isinstance(msg, HumanMessage):
                    self._summary_memory.chat_memory.add_user_message(msg.content)
                elif isinstance(msg, AIMessage):
                    self._summary_memory.chat_memory.add_ai_message(msg.content)
            return self._summary_memory.buffer
        except Exception:
            return None

    def get_context_for_prompt(self) -> str:
        parts = []
        summary = self.get_summary()
        if summary:
            parts.append(f"## 对话历史摘要\n{summary}")
        return "\n\n".join(parts)
