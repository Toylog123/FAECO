@echo off
rem 中文论文编译入口：调用 compile.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0compile.ps1" %*
exit /b %errorlevel%
