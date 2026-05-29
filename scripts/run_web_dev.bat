@echo off
cd /d %~dp0..
start "api" cmd /k "python -m uvicorn backend.api.main:app --reload --host 127.0.0.1 --port 8000"
cd frontend
npm run dev
