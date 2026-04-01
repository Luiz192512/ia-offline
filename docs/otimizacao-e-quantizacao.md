# Otimizacao e Quantizacao

## Objetivo

A meta principal e manter boa usabilidade em CPU comum, respeitando o limite de armazenamento e memoria de um pendrive de 32 GB.

## Escolha de quantizacao

- 4-bit:
  melhor equilibrio entre tamanho e velocidade para a maioria dos cenarios offline.

- 5-bit:
  ocupa mais espaco e RAM, mas pode melhorar a qualidade em tarefas tecnicas.

- 8-bit:
  use apenas quando houver bastante RAM disponivel; costuma ser pesado para o objetivo portatil.

## Ajustes praticos no projeto

- `model.context_window`:
  mantenha em `2048` para hardware limitado. Suba apenas se o equipamento suportar.

- `model.max_tokens`:
  reduza para `128` ou `192` quando quiser respostas mais rapidas.

- `memory.max_turns`:
  mantenha entre `4` e `6` para evitar crescimento desnecessario do prompt.

- `runner.extra_args`:
  adicione aqui flags especificas da sua build do `llama.cpp`, se necessario.

- `-ngl 0`:
  mantem execucao em CPU pura, sem depender de GPU.

## Recomendacao de armazenamento

- aplicacao e scripts:
  menos de 50 MB

- runtime:
  varia conforme a build, normalmente pequeno perto do modelo

- modelo GGUF:
  priorize manter entre 4 GB e 8 GB para preservar folga no pendrive

## Estrategia de desempenho

1. Comece com quantizacao 4-bit.
2. Use contexto de 2048.
3. Reduza `max_tokens` se a latencia estiver alta.
4. So aumente contexto ou quantizacao quando o hardware responder bem.
