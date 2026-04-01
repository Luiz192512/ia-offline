# Modelos GGUF

Coloque aqui o arquivo do modelo quantizado, por exemplo:

```text
models/model.gguf
```

Sugestoes de perfil:

- 4-bit para melhor equilibrio entre tamanho e velocidade
- 5-bit quando houver RAM um pouco maior e voce quiser ganhar qualidade
- contexto de 2048 para hardware mais limitado

Depois de copiar o modelo, ajuste `model.path` se o nome do arquivo for diferente.
