# Validacao Offline

## Objetivos de teste

- Confirmar que o sistema inicializa sem internet.
- Confirmar que o modelo e o runtime sao encontrados.
- Validar uso em CPU sem GPU obrigatoria.
- Confirmar que a interface permanece simples e responsiva.
- Verificar se o contexto curto e mantido sem crescimento descontrolado.

## Checklist operacional

1. Desconectar a rede ou usar um ambiente sem internet.
2. Rodar `python -m app.main --status`.
3. Rodar `scripts/verify_offline.ps1` no Windows ou `scripts/verify_offline.sh` no Linux.
4. Abrir a CLI e testar:
   - pergunta geral
   - pergunta tecnica
   - pedido de codigo
   - sequencia curta de perguntas para validar memoria
5. Abrir a GUI e repetir um caso simples.
6. Conferir se a base local em `knowledge_base/` aparece nas respostas quando pertinente.

## Testes sugeridos

- Pergunta geral:
  "Explique o que e compressao de modelos em linguagem simples."

- Pergunta tecnica:
  "Crie um exemplo em Python para ler um arquivo JSON."

- Pergunta operacional:
  "Como reduzir o uso de memoria deste sistema em CPU?"

- Memoria curta:
  perguntar um nome, depois referenciar esse nome em uma pergunta seguinte.

## Criterios de aceitacao

- O app abre sem depender de rede.
- O status informa claramente se falta modelo ou executavel.
- O sistema responde sem travar a interface.
- O consumo de disco cabe no limite do pendrive.
- O comportamento informa limitacoes em vez de inventar fatos.
