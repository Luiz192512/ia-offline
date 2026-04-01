from __future__ import annotations

from .assistant import OfflineAssistant

HELP_TEXT = """Comandos disponiveis:
/ajuda   mostra esta ajuda
/status  mostra o estado do runtime
/limpar  limpa a memoria da sessao
/sair    encerra o programa
"""


def _format_status(assistant: OfflineAssistant) -> str:
    status = assistant.status()
    lines = [
        f"App: {status['app']}",
        f"Pronto: {status['ready']}",
        f"Status: {status['message']}",
        f"Modelo: {status['model']}",
        f"Executavel: {status['executable']}",
        f"Memoria curta: {status['memory_turns']} turnos",
        f"Base local: {status['knowledge_base']}",
    ]
    return "\n".join(lines)


def run_cli(assistant: OfflineAssistant) -> int:
    print("IA Offline Portatil")
    print("Digite /ajuda para ver os comandos.\n")

    while True:
        try:
            user_input = input("Voce> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando.")
            return 0

        if not user_input:
            continue

        if user_input == "/sair":
            print("Encerrando.")
            return 0
        if user_input == "/ajuda":
            print(HELP_TEXT)
            continue
        if user_input == "/status":
            print(_format_status(assistant))
            print()
            continue
        if user_input == "/limpar":
            assistant.clear()
            print("Memoria da sessao limpa.\n")
            continue

        response = assistant.respond(user_input)
        print(f"\nIA> {response.text}\n")

        if response.sources:
            source_names = ", ".join(snippet.path.name for snippet in response.sources)
            print(f"Fontes locais consultadas: {source_names}\n")

    return 0
