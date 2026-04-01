from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime

from .config import AppConfig
from .engine import EngineConfigurationError, LlamaCppEngine
from .kb import KnowledgeBase, KnowledgeSnippet
from .memory import ConversationMemory
from .prompting import build_prompt, load_text_file


@dataclass(slots=True)
class AssistantResponse:
    text: str
    sources: list[KnowledgeSnippet]
    degraded: bool


class OfflineAssistant:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.engine = LlamaCppEngine(config.runner, config.model)
        self.memory = ConversationMemory(
            max_turns=config.memory.max_turns,
            max_chars=config.memory.max_chars,
        )
        self.knowledge_base = KnowledgeBase(config.knowledge_base)
        self.system_prompt = load_text_file(config.prompt.resolved_system_prompt_file)
        self.session_log_path = self._build_log_path()

    def _build_log_path(self) -> str | None:
        if not self.config.logging.enabled:
            return None

        directory = self.config.logging.resolved_directory
        directory.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return str(directory / f"session-{stamp}.jsonl")

    def clear(self) -> None:
        self.memory.clear()

    def status(self) -> dict[str, str | bool | int]:
        engine_status = self.engine.status()
        return {
            "app": self.config.app.name,
            "ready": engine_status.ready,
            "message": engine_status.message,
            "model": engine_status.model,
            "executable": engine_status.executable,
            "memory_turns": self.config.memory.max_turns,
            "knowledge_base": str(self.config.knowledge_base.resolved_directory),
        }

    def respond(self, user_input: str) -> AssistantResponse:
        snippets = self.knowledge_base.search(user_input)
        knowledge_context = self.knowledge_base.format_for_prompt(snippets)
        transcript = self.memory.to_transcript()
        prompt = build_prompt(
            system_prompt=self.system_prompt,
            knowledge_context=knowledge_context,
            transcript=transcript,
            user_input=user_input,
            assistant_suffix=self.config.prompt.assistant_suffix,
        )

        degraded = False
        try:
            answer = self.engine.generate(prompt)
        except EngineConfigurationError as exc:
            degraded = True
            answer = self._diagnostic_message(str(exc))
        except Exception as exc:  # noqa: BLE001
            degraded = True
            answer = (
                "Ocorreu uma falha ao executar o runtime local.\n\n"
                f"Detalhe: {exc}\n\n"
                "Verifique o modelo GGUF, o executavel do llama.cpp e os caminhos em "
                "`config/default_config.json` ou `config/local_config.json`."
            )

        self.memory.add("user", user_input)
        self.memory.add("assistant", answer)
        self._append_log(user_input=user_input, answer=answer, degraded=degraded, sources=snippets)

        return AssistantResponse(text=answer, sources=snippets, degraded=degraded)

    def _diagnostic_message(self, reason: str) -> str:
        return (
            "O assistente entrou em modo diagnostico porque o runtime offline ainda nao esta completo.\n\n"
            f"Motivo: {reason}\n\n"
            "Para concluir a configuracao:\n"
            "1. Coloque um modelo `.gguf` na pasta `models/`.\n"
            "2. Coloque o executavel do `llama.cpp` em `runtime/llama.cpp/windows/` ou "
            "`runtime/llama.cpp/linux/`.\n"
            "3. Ajuste os caminhos no arquivo `config/local_config.json`, se necessario.\n"
            "4. Rode `python -m app.main --status` para validar novamente."
        )

    def _append_log(
        self,
        *,
        user_input: str,
        answer: str,
        degraded: bool,
        sources: list[KnowledgeSnippet],
    ) -> None:
        if not self.session_log_path:
            return

        payload = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "answer": answer,
            "degraded": degraded,
            "sources": [str(snippet.path) for snippet in sources],
        }

        with open(self.session_log_path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
