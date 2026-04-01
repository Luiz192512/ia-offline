# Runtime local

Estrutura esperada:

```text
runtime/
`-- llama.cpp/
    |-- windows/
    |   `-- llama-cli.exe
    `-- linux/
        `-- llama-cli
```

Coloque aqui o binario compilado do `llama.cpp` correspondente ao sistema operacional alvo.

Se o nome do executavel for diferente, ajuste:

- `runner.executable_windows`
- `runner.executable_linux`

Tambem e possivel ajustar os argumentos do processo em `config/default_config.json`.
