from __future__ import annotations

import subprocess
from dataclasses import dataclass

from .config import ModelConfig, RunnerConfig


class EngineConfigurationError(RuntimeError):
    """Problema de configuracao do runtime offline."""


@dataclass(slots=True)
class EngineStatus:
    ready: bool
    message: str
    executable: str
    model: str


class LlamaCppEngine:
    def __init__(self, runner_config: RunnerConfig, model_config: ModelConfig) -> None:
        self.runner_config = runner_config
        self.model_config = model_config

    def status(self) -> EngineStatus:
        executable = self.runner_config.resolved_executable
        model = self.model_config.resolved_model_path
        issues: list[str] = []

        if not executable.exists():
            issues.append(f"executavel ausente: {executable}")
        if not model.exists():
            issues.append(f"modelo ausente: {model}")

        if issues:
            return EngineStatus(
                ready=False,
                message="Configuracao incompleta: " + "; ".join(issues),
                executable=str(executable),
                model=str(model),
            )

        return EngineStatus(
            ready=True,
            message="Runtime offline pronto para inferencia.",
            executable=str(executable),
            model=str(model),
        )

    def build_command(self, prompt: str) -> list[str]:
        executable = self.runner_config.resolved_executable
        values = {
            "model": str(self.model_config.resolved_model_path),
            "context_window": str(self.model_config.context_window),
            "max_tokens": str(self.model_config.max_tokens),
            "temperature": str(self.model_config.temperature),
            "top_k": str(self.model_config.top_k),
            "top_p": str(self.model_config.top_p),
            "repeat_penalty": str(self.model_config.repeat_penalty),
            "prompt": prompt,
        }

        args = [
            item.format_map(values)
            for item in [*self.runner_config.base_args, *self.runner_config.extra_args]
        ]
        return [str(executable), *args]

    def generate(self, prompt: str) -> str:
        status = self.status()
        if not status.ready:
            raise EngineConfigurationError(status.message)

        completed = subprocess.run(
            self.build_command(prompt),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=self.runner_config.timeout_seconds,
            check=False,
        )

        if completed.returncode != 0:
            stderr = completed.stderr.strip() or "falha sem detalhes no stderr"
            raise RuntimeError(f"O runtime retornou erro: {stderr}")

        return self._clean_output(completed.stdout, prompt)

    @staticmethod
    def _clean_output(raw_output: str, prompt: str) -> str:
        output = raw_output.strip()

        if output.startswith(prompt.strip()):
            output = output[len(prompt.strip()) :].strip()

        for marker in ("### ASSISTENTE", "Assistente:", "ASSISTENTE:"):
            if marker in output:
                output = output.split(marker, 1)[-1].strip()

        return output or "Nao houve resposta gerada pelo runtime local."
