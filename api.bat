@echo off
set TANAKAI=%~dp0
cd server && uvicorn main:app --reload