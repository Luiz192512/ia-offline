# IA Offline Portatil

Projeto base para um assistente conversacional offline executavel a partir de um pendrive de 32 GB, com foco em CPU, portabilidade e simplicidade de operacao.

## Objetivo

Entregar uma experiencia semelhante a um assistente conversacional moderno, mas adaptada a:

- Execucao totalmente offline
- Janela de contexto curta
- Uso em hardware comum, sem GPU obrigatoria
- Armazenamento limitado em pendrive
- Conhecimento embarcado local em arquivos

## O que este MVP entrega

- Nucleo local em Python com zero dependencias externas obrigatorias
- Integracao por subprocesso com `llama.cpp`
- Memoria curta de conversa
- Recuperacao simples de conhecimento local em `knowledge_base/`
- Interface CLI
- Interface grafica leve em Tkinter
- Scripts de inicializacao para Windows e Linux
- Verificacao rapida de prontidao offline

## Estrutura

```text
ia-offline/
|-- app/                     # Codigo principal
|-- config/                  # Prompt e configuracao padrao
|-- docs/                    # Arquitetura e validacao
|-- knowledge_base/          # Conteudo local embarcado
|-- models/                  # Coloque aqui o modelo GGUF
|-- runtime/llama.cpp/       # Binarios do llama.cpp
|-- scripts/                 # Launchers e verificacao
`-- tests/                   # Testes basicos
```

## Como preparar o pendrive

1. Copie esta pasta inteira para o pendrive.
2. Coloque um modelo `.gguf` em `models/`.
3. Coloque o binario do `llama.cpp` em `runtime/llama.cpp/`.
4. Opcionalmente crie `config/local_config.json` a partir de `config/local_config.example.json`.
5. Execute um dos launchers em `scripts/`.

## Recomendacao pratica para 32 GB

- Reserve de 4 GB a 8 GB para o modelo GGUF.
- Reserve menos de 1 GB para o runtime e a aplicacao.
- Deixe espaco livre para logs, base local e documentos.
- Prefira quantizacao 4-bit ou 5-bit para CPU comum.

Perfis usuais:

- Leve: modelo pequeno quantizado, contexto de 2048 tokens
- Balanceado: modelo medio quantizado, contexto de 2048 a 4096 tokens
- Conservador: reduzir `max_tokens` e manter `-ngl 0` para CPU pura

## Execucao

### Windows

CLI:

```powershell
.\scripts\run_cli.bat
```

GUI:

```powershell
.\scripts\run_gui.bat
```

Diagnostico:

```powershell
python -m app.main --status
.\scripts\verify_offline.ps1
```

### Linux

CLI:

```bash
./scripts/run_cli.sh
```

GUI:

```bash
./scripts/run_gui.sh
```

Diagnostico:

```bash
python3 -m app.main --status
./scripts/verify_offline.sh
```

## Ajustes importantes

Arquivo principal de configuracao:

- `config/default_config.json`

Pontos que normalmente voce ajusta:

- `model.path`
- `runner.executable_windows`
- `runner.executable_linux`
- `model.context_window`
- `model.max_tokens`
- `memory.max_turns`

Se quiser deixar o pendrive mais autonomo, voce tambem pode embarcar um Python portatil em `portable/python/`.

## Limites assumidos

- O sistema nao usa internet
- O conhecimento vem do modelo GGUF e dos arquivos locais
- A memoria e de curta duracao e limitada a sessao atual
- Se o modelo ou o runtime nao estiverem presentes, o app entra em modo diagnostico orientado

## Validacao rapida

1. Rode `python -m app.main --status`.
2. Confirme que o executavel e o modelo foram encontrados.
3. Rode `.\scripts\verify_offline.ps1` ou `./scripts/verify_offline.sh`.
4. Teste perguntas curtas, tecnicas e operacionais.
5. Valide se o tempo de resposta esta aceitavel no hardware alvo.

## Documentacao complementar

- `docs/arquitetura.md`
- `docs/validacao-offline.md`
- `docs/otimizacao-e-quantizacao.md`
