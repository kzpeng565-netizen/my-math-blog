@echo off
chcp 65001 >nul
title 卸载 Quartz Reminder Engine 自启动

echo ╔═══════════════════════════════════════════╗
echo ║   卸载 Windows 开机自启动任务提醒          ║
echo ╚═══════════════════════════════════════════╝
echo.

:: 删除计划任务
schtasks /delete /tn "QuartzReminderEngine" /f

if %ERRORLEVEL% EQU 0 (
    echo [成功] 已删除计划任务 "QuartzReminderEngine"
) else (
    echo [警告] 删除计划任务失败（可能不存在）
)

echo.
echo 提醒引擎文件仍然保留，您可以手动运行 start-reminder.bat 启动。
echo 如需完全删除，请删除 reminder-engine 文件夹。
echo.
pause