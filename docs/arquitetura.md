# Arquitetura do MVP

## Visao geral

O sistema foi estruturado para rodar localmente em Windows ou Linux diretamente do pendrive, com dependencia principal de um modelo GGUF e de um executavel do `llama.cpp`.

Fluxo principal:

1. A interface recebe a pergunta do usuario.
2. O nucleo consulta a memoria curta da sessao.
3. O modulo de base local busca arquivos relevantes em `knowledge_base/`.
4. O prompt final e montado com:
   - instrucoes de sistema
   - contexto local recuperado
   - historico recente
   - pergunta atual
5. O runtime `llama.cpp` e executado por subprocesso.
6. A resposta retorna para a CLI ou GUI.

## Modulos

- `app/config.py`: carrega a configuracao padrao e overrides locais.
- `app/memory.py`: mantem a janela curta de conversa.
- `app/kb.py`: recupera documentos locais por sobreposicao simples de termos.
- `app/prompting.py`: compoe o prompt final.
- `app/engine.py`: integra com o executavel do `llama.cpp`.
- `app/assistant.py`: orquestra memoria, conhecimento local, runtime e logging.
- `app/ui_cli.py`: terminal interativo.
- `app/ui_gui.py`: interface grafica leve em Tkinter.

## Decisoes de projeto

- Python com biblioteca padrao:
  reduz complexidade de instalacao no pendrive.

- `llama.cpp` por subprocesso:
  evita dependencia pesada de bindings locais e facilita portabilidade.

- GGUF quantizado:
  permite equilibrio entre qualidade, RAM e armazenamento.

- Memoria curta:
  mantem previsibilidade de consumo e latencia.

- Recuperacao lexical simples:
  funciona 100% offline, sem vetor DB ou servicos auxiliares.

## Limites conhecidos

- Nao ha conhecimento online nem atualizacao automatica.
- A recuperacao local e simples e nao substitui um RAG completo.
- A qualidade final depende fortemente do modelo GGUF escolhido.
- O formato de argumentos do `llama.cpp` pode variar entre builds; por isso os caminhos e argumentos estao centralizados em configuracao.
