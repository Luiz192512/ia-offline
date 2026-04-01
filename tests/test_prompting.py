import unittest

from app.prompting import build_prompt


class PromptingTests(unittest.TestCase):
    def test_prompt_contains_expected_sections(self) -> None:
        prompt = build_prompt(
            system_prompt="Sistema",
            knowledge_context="Fonte local",
            transcript="Usuario: oi",
            user_input="Explique isso",
            assistant_suffix="Seja claro",
        )

        self.assertIn("### SISTEMA", prompt)
        self.assertIn("### CONHECIMENTO LOCAL RELEVANTE", prompt)
        self.assertIn("### HISTORICO RECENTE", prompt)
        self.assertIn("### USUARIO", prompt)
        self.assertTrue(prompt.rstrip().endswith("### ASSISTENTE"))


if __name__ == "__main__":
    unittest.main()
