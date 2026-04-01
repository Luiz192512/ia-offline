from __future__ import annotations

from pathlib import Path


def load_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def build_prompt(
    *,
    system_prompt: str,
    knowledge_context: str,
    transcript: str,
    user_input: str,
    assistant_suffix: str,
) -> str:
    sections = [
        "### SISTEMA",
        system_prompt.strip(),
    ]

    if knowledge_context.strip():
        sections.extend(
            [
                "",
                "### CONHECIMENTO LOCAL RELEVANTE",
                knowledge_context.strip(),
            ]
        )

    if transcript.strip():
        sections.extend(
            [
                "",
                "### HISTORICO RECENTE",
                transcript.strip(),
            ]
        )

    sections.extend(
        [
            "",
            "### USUARIO",
            user_input.strip(),
            "",
            "### INSTRUCAO FINAL",
            assistant_suffix.strip(),
            "",
            "### ASSISTENTE",
        ]
    )

    return "\n".join(sections).strip() + "\n"
