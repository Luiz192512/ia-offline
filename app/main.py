from __future__ import annotations

import argparse

from .assistant import OfflineAssistant
from .config import load_config
from .ui_cli import run_cli
from .ui_gui import run_gui


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="IA Offline Portatil")
    parser.add_argument("--mode", choices=("cli", "gui"), default="cli")
    parser.add_argument("--config", help="Caminho de override JSON de configuracao")
    parser.add_argument("--status", action="store_true", help="Mostra o estado do runtime e sai")
    return parser


def _print_status(assistant: OfflineAssistant) -> None:
    status = assistant.status()
    for key, value in status.items():
        print(f"{key}: {value}")


def main() -> int:
    args = _build_parser().parse_args()
    config = load_config(args.config)
    assistant = OfflineAssistant(config)

    if args.status:
        _print_status(assistant)
        return 0

    if args.mode == "gui":
        return run_gui(assistant)

    return run_cli(assistant)


if __name__ == "__main__":
    raise SystemExit(main())
