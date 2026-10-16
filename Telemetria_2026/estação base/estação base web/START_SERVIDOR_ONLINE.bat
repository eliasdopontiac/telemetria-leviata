@echo off
title Telemetria Leviata 2026 - Servidor Central Online (Computador A)
color 0E
echo =================================================================
echo   🚤 TELEMETRIA LEVIATÃ 2026 - SERVIDOR CENTRAL (COMPUTADOR A)
echo =================================================================
echo   Iniciando o servidor central com Tunel Cloudflare e Notificacao.
echo   - Recebe dados do Computador B via rota /api/ingest
echo   - Retransmite via Socket.IO para qualquer espectador na internet.
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


:: Verifica se as dependencias existem, senao instala
if not exist "node_modules\express" (
  echo Primeira execucao detectada: Instalando dependencias do backend...
  call npm install
  if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar dependencias com npm.
    echo Certifique-se de que o Node.js esta instalado nesta maquina.
    pause
    exit /b
  )
)

:: Libera a porta 3001 caso haja uma instancia anterior presa
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3001" ^| findstr "LISTENING"') do (
  taskkill /f /pid %%a >nul 2>&1
)

:: Inicia o backend Node.js
start "Servidor Node.js - Central" "%NODE_EXE%" server.js

:: Inicia o gerenciador de tunel Cloudflare com notificacao por e-mail
echo Aguardando inicializacao do servidor local...
timeout /t 3 /nobreak >nul

"%NODE_EXE%" notificador_tunnel.js
pause
