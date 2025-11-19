@echo off
cd /d "%~dp0"
:: %* passes all arguments exactly as received, preserving quotes
uv run run_cli.py %*
