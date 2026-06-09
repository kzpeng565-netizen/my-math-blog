@echo off
chcp 65001 >nul
title 安装 Quartz Reminder Engine 自启动

echo ╔═══════════════════════════════════════════╗
echo ║   安装 Windows 开机自启动任务提醒          ║
echo ╚═══════════════════════════════════════════╝
echo.

:: 获取当前目录的完整路径
set "SCRIPT_DIR=%~dp0"
set "NODE_EXE=node.exe"

:: 寻找 node.exe
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 未找到 Node.js，请先安装 Node.js
    pause
    exit /b 1
)

for /f "delims=" %%i in ('where node') do set "NODE_PATH=%%i"

echo 找到 Node.js: %NODE_PATH%
echo 提醒引擎目录: %SCRIPT_DIR%
echo.

:: 创建 Windows 计划任务（用户登录时启动）
schtasks /create /tn "QuartzReminderEngine" /tr "'%NODE_PATH%' '%SCRIPT_DIR%reminder-engine.mjs'" /sc onlogon /delay 0000:30 /rl limited /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [成功] 已创建计划任务 "QuartzReminderEngine"
    echo 将在您每次登录 Windows 30 秒后自动启动提醒引擎。
    echo.
    echo 要立即启动，请运行: start-reminder.bat
    echo 要卸载自启动，请运行: uninstall-autostart.bat
) else (
    echo.
    echo [警告] 创建计划任务失败。
    echo 请尝试以管理员身份运行此脚本。
    echo.
    echo 您仍然可以手动运行 start-reminder.bat 来启动提醒引擎。
)

echo.
pause