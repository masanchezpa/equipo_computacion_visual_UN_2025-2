# Script para ejecutar la interfaz gráfica
# Ejecutar con: .\run_gui.ps1

Write-Host "Iniciando Asistente Visual Auditivo..." -ForegroundColor Green
Set-Location $PSScriptRoot
& .\.venv\Scripts\python.exe gui_app.py

