@echo off
echo Starting Scryfall MCP Server (SSE mode on http://127.0.0.1:8000)...
cd /d "%~dp0"
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe server.py --transport sse --port 8000
) else (
    python server.py --transport sse --port 8000
)
pause
