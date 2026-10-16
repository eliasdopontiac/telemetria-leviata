@echo off
title Telemetria Leviata 2026 - Estacao Base Pista (Portatil)
color 0A
echo =================================================================
echo   🚤 TELEMETRIA LEVIATÃ 2026 - ESTAÇÃO BASE DE PISTA (PORTÁTIL)
echo =================================================================
echo   Iniciando o servidor central (Serial + SQLite + Socket.IO)...
echo   O navegador sera aberto automaticamente em http://localhost:3001
echo.
echo   Qualquer outro dispositivo na mesma rede Wi-Fi pode acessar
echo   usando o IP deste computador na porta :3001
echo =================================================================
echo.

set "NODE_EXE=%~dp0node\node.exe"
if not exist "%NODE_EXE%" set "NODE_EXE=node"

cd /d "%~dp0backend-node"

:: Recompila o frontend (se as dependencias existirem) para refletir as ultimas alteracoes
if exist "..\frontend-react\node_modules" (
  where npm >nul 2>&1
  if not errorlevel 1 (
    echo Recompilando o frontend...
    pushd "..\frontend-react"
    call npm run build
    popd
  )
)

:: Libera a porta 3001 caso haja uma instancia anterior presa
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3001" ^| findstr "LISTENING"') do (
  taskkill /f /pid %%a >nul 2>&1
)

"%NODE_EXE%" server.js
pause
