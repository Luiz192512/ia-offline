from __future__ import annotations

import json
import platform
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "default_config.json"


def resolve_project_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return (PROJECT_ROOT / path).resolve()


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            merged[key] = _deep_merge(base[key], value)
        else:
            merged[key] = value
    return merged


def _load_json_file(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@dataclass(slots=True)
class AppMetaConfig:
    name: str
    language: str


@dataclass(slots=True)
class ModelConfig:
    path: str
    context_window: int
    max_tokens: int
    temperature: float
    top_k: int
    top_p: float
    repeat_penalty: float

    @property
    def resolved_model_path(self) -> Path:
        return resolve_project_path(self.path)


@dataclass(slots=True)
class RunnerConfig:
    backend: str
    executable_windows: str
    executable_linux: str
    base_args: list[str] = field(default_factory=list)
    extra_args: list[str] = field(default_factory=list)
    timeout_seconds: int = 120

    @property
    def resolved_executable(self) -> Path:
        system_name = platform.system().lower()
        raw = self.executable_windows if system_name.startswith("win") else self.executable_linux
        return resolve_project_path(raw)


@dataclass(slots=True)
class MemoryConfig:
    max_turns: int
    max_chars: int


@dataclass(slots=True)
class KnowledgeBaseConfig:
    directory: str
    max_files: int
    max_chars_per_file: int
    enabled_extensions: list[str]

    @property
    def resolved_directory(self) -> Path:
        return resolve_project_path(self.directory)


@dataclass(slots=True)
class PromptConfig:
    system_prompt_file: str
    assistant_suffix: str

    @property
    def resolved_system_prompt_file(self) -> Path:
        return resolve_project_path(self.system_prompt_file)


@dataclass(slots=True)
class LoggingConfig:
    enabled: bool
    directory: str

    @property
    def resolved_directory(self) -> Path:
        return resolve_project_path(self.directory)


@dataclass(slots=True)
class AppConfig:
    app: AppMetaConfig
    model: ModelConfig
    runner: RunnerConfig
    memory: MemoryConfig
    knowledge_base: KnowledgeBaseConfig
    prompt: PromptConfig
    logging: LoggingConfig


def load_config(config_path: str | None = None) -> AppConfig:
    raw = _load_json_file(DEFAULT_CONFIG_PATH)

    if config_path:
        raw = _deep_merge(raw, _load_json_file(resolve_project_path(config_path)))
    else:
        local_config = PROJECT_ROOT / "config" / "local_config.json"
        if local_config.exists():
            raw = _deep_merge(raw, _load_json_file(local_config))

    return AppConfig(
        app=AppMetaConfig(**raw["app"]),
        model=ModelConfig(**raw["model"]),
        runner=RunnerConfig(**raw["runner"]),
        memory=MemoryConfig(**raw["memory"]),
        knowledge_base=KnowledgeBaseConfig(**raw["knowledge_base"]),
        prompt=PromptConfig(**raw["prompt"]),
        logging=LoggingConfig(**raw["logging"]),
    )
