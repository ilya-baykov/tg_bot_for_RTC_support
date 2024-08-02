@echo off
set PYTHONUNBUFFERED=1
set JSON_PATH=C:\BOT\database\calendar_export.json
set LOGS_PATH=C:\BOT\LOGS
set TOKEN=7405453506:AAGfvbxVrGJa2tW_cG583hS637pG-TZLTHQ
set PYTHONPATH=C:\BOT
pushd C:\BOT
C:\BOT\venv\Scripts\python.exe run_app\main.py
popd
