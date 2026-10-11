@echo off
title Telemetria Leviata 2026 - Pista Online (Computador B)
color 0B
echo =================================================================
echo   🚤 TELEMETRIA LEVIATÃ 2026 - PISTA ONLINE (COMPUTADOR B)
echo =================================================================
echo   Modo com UPLINK ATIVO para Sincronizacao Online com Servidor A.
echo   - Se a internet cair, todos os dados continuam salvos localmente.
echo   - Assim que a conexao voltar, a fila sincroniza automaticamente.
echo.
echo   O painel local sera aberto em http://localhost:3001
echo   Use o botao "Online Sync" no topo para colar a URL do Computador A.
echo =================================================================
echo.

set "NODE_EXE=%~dp0node\node.exe"
if not exist "%NODE_EXE%" set "NODE_EXE=node"

cd /d "%~dp0backend-node"

:: Verifica se as dependencias existem, senao instala
if not exist "node_modules\express" (
  echo Primeira execucao detectada: Instalando dependencias do backend...
  call npm install
  if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar dependencias com npm.
    pause
    exit /b
  )
)

set MODO_ONLINE=true
"%NODE_EXE%" server.js
pause
