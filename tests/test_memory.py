import unittest

from app.memory import ConversationMemory


class MemoryTests(unittest.TestCase):
    def test_memory_keeps_recent_messages(self) -> None:
        memory = ConversationMemory(max_turns=2, max_chars=1000)
        memory.add("user", "pergunta 1")
        memory.add("assistant", "resposta 1")
        memory.add("user", "pergunta 2")
        memory.add("assistant", "resposta 2")
        memory.add("user", "pergunta 3")
        memory.add("assistant", "resposta 3")

        transcript = memory.to_transcript()
        self.assertNotIn("pergunta 1", transcript)
        self.assertIn("resposta 3", transcript)


if __name__ == "__main__":
    unittest.main()
