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

:: Inicia o backend Node.js
start "Servidor Node.js - Central" "%NODE_EXE%" server.js

:: Inicia o gerenciador de tunel Cloudflare com notificacao por e-mail
echo Aguardando inicializacao do servidor local...
timeout /t 3 /nobreak >nul

"%NODE_EXE%" notificador_tunnel.js
pause
