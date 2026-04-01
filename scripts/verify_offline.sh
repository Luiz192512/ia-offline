#!/usr/bin/env sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
ROOT_DIR="$SCRIPT_DIR/.."
MODEL_PATH="$ROOT_DIR/models/model.gguf"
WINDOWS_EXE="$ROOT_DIR/runtime/llama.cpp/windows/llama-cli.exe"
LINUX_EXE="$ROOT_DIR/runtime/llama.cpp/linux/llama-cli"

echo "Validando ambiente offline em $ROOT_DIR"

if command -v python3 >/dev/null 2>&1; then
  echo "[OK] Python3 encontrado"
else
  echo "[ERRO] Python3 nao encontrado"
fi

if [ -f "$MODEL_PATH" ]; then
  echo "[OK] Modelo encontrado: $MODEL_PATH"
else
  echo "[ALERTA] Modelo nao encontrado: $MODEL_PATH"
fi

if [ -f "$WINDOWS_EXE" ]; then
  echo "[OK] Executavel Windows encontrado: $WINDOWS_EXE"
else
  echo "[ALERTA] Executavel Windows nao encontrado: $WINDOWS_EXE"
fi

if [ -f "$LINUX_EXE" ]; then
  echo "[OK] Executavel Linux encontrado: $LINUX_EXE"
else
  echo "[ALERTA] Executavel Linux nao encontrado: $LINUX_EXE"
fi

echo "Diagnostico concluido."
