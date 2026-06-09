@echo off
chcp 65001 >nul
title Quartz Reminder Engine - 任务提醒引擎

echo.
echo ╔═══════════════════════════════════════════╗
echo ║    Quartz Reminder Engine - 任务提醒引擎   ║
echo ╚═══════════════════════════════════════════╝
echo.
echo 启动提醒引擎...
echo 按 Ctrl+C 停止
echo.

cd /d "%~dp0"
node reminder-engine.mjs

pause