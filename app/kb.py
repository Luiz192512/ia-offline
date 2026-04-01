from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .config import KnowledgeBaseConfig

TOKEN_RE = re.compile(r"[a-zA-Z0-9_]{2,}")


def _tokenize(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(text)}


@dataclass(slots=True)
class KnowledgeSnippet:
    path: Path
    score: int
    excerpt: str


class KnowledgeBase:
    def __init__(self, config: KnowledgeBaseConfig) -> None:
        self.config = config

    def _load_text(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return path.read_text(encoding="latin-1", errors="replace")

    def _iter_documents(self) -> list[Path]:
        directory = self.config.resolved_directory
        if not directory.exists():
            return []

        enabled = set(self.config.enabled_extensions)
        return [
            path
            for path in sorted(directory.rglob("*"))
            if path.is_file() and path.suffix.lower() in enabled
        ]

    def search(self, query: str) -> list[KnowledgeSnippet]:
        documents = self._iter_documents()
        if not documents:
            return []

        query_tokens = _tokenize(query)
        ranked: list[KnowledgeSnippet] = []

        for path in documents:
            raw_text = self._load_text(path).strip()
            if not raw_text:
                continue

            score = len(query_tokens & _tokenize(raw_text))
            excerpt = raw_text[: self.config.max_chars_per_file]
            ranked.append(KnowledgeSnippet(path=path, score=score, excerpt=excerpt))

        ranked.sort(key=lambda item: (item.score, item.path.name.lower()), reverse=True)
        selected = [item for item in ranked if item.score > 0][: self.config.max_files]
        if selected:
            return selected
        return ranked[: self.config.max_files]

    @staticmethod
    def format_for_prompt(snippets: list[KnowledgeSnippet]) -> str:
        if not snippets:
            return ""

        chunks: list[str] = []
        for snippet in snippets:
            chunks.append(f"Fonte: {snippet.path.name}\n{snippet.excerpt}")
        return "\n\n".join(chunks)
