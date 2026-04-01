$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$modelPath = Join-Path $root "models\model.gguf"
$windowsExe = Join-Path $root "runtime\llama.cpp\windows\llama-cli.exe"
$linuxExe = Join-Path $root "runtime\llama.cpp\linux\llama-cli"

Write-Host "Validando ambiente offline em $root"

if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "[OK] Python encontrado"
}
else {
    Write-Host "[ERRO] Python nao encontrado"
}

if (Test-Path $modelPath) {
    Write-Host "[OK] Modelo encontrado: $modelPath"
}
else {
    Write-Host "[ALERTA] Modelo nao encontrado: $modelPath"
}

if (Test-Path $windowsExe) {
    Write-Host "[OK] Executavel Windows encontrado: $windowsExe"
}
else {
    Write-Host "[ALERTA] Executavel Windows nao encontrado: $windowsExe"
}

if (Test-Path $linuxExe) {
    Write-Host "[OK] Executavel Linux encontrado: $linuxExe"
}
else {
    Write-Host "[ALERTA] Executavel Linux nao encontrado: $linuxExe"
}

Write-Host "Diagnostico concluido."
