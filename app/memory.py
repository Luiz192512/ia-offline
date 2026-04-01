from __future__ import annotations

from dataclasses import dataclass


ROLE_LABELS = {
    "user": "Usuario",
    "assistant": "Assistente",
    "system": "Sistema",
}


@dataclass(slots=True)
class ChatMessage:
    role: str
    content: str


class ConversationMemory:
    def __init__(self, max_turns: int, max_chars: int) -> None:
        self.max_turns = max_turns
        self.max_chars = max_chars
        self.messages: list[ChatMessage] = []

    def clear(self) -> None:
        self.messages.clear()

    def add(self, role: str, content: str) -> None:
        clean = content.strip()
        if not clean:
            return
        self.messages.append(ChatMessage(role=role, content=clean))
        self._trim()

    def _trim(self) -> None:
        max_messages = max(self.max_turns * 2, 2)
        while len(self.messages) > max_messages:
            self.messages.pop(0)

        while self.total_chars > self.max_chars and len(self.messages) > 2:
            self.messages.pop(0)

    @property
    def total_chars(self) -> int:
        return sum(len(message.content) for message in self.messages)

    def to_transcript(self) -> str:
        lines: list[str] = []
        for message in self.messages:
            label = ROLE_LABELS.get(message.role, message.role.title())
            lines.append(f"{label}: {message.content}")
        return "\n".join(lines)
