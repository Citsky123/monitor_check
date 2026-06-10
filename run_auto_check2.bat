@echo off
chcp 65001 >nul
title 自动点检系统运行脚本

:: ===================== 配置区 =====================
set PYTHON_EXE=D:\Python313\python.exe
set SCRIPT_DIR=D:\VScode\check
set SCRIPT_NAME=auto_check2.py
set LOG_FILE=auto_check2_log.txt
:: ==============================================

:: 1. 切换到脚本目录
cd /d "%SCRIPT_DIR%"
if %errorlevel% neq 0 (
    echo [%time%] [ERROR] 切换目录失败：%SCRIPT_DIR% 不存在！
    pause
    exit /b 1
)

:: 2. 记录开始日志（使用 time 变量避免中文日期问题）
echo ====================================================== >> "%LOG_FILE%" 2>&1
echo [%time%] [INFO] 脚本开始运行 >> "%LOG_FILE%" 2>&1

:: 3. 运行Python脚本并捕获退出码
"%PYTHON_EXE%" -u "%SCRIPT_NAME%" >> "%LOG_FILE%" 2>&1
set EXIT_CODE=%errorlevel%

:: 4. 记录结束日志
echo [%time%] [INFO] 脚本运行结束，退出码：%EXIT_CODE% >> "%LOG_FILE%" 2>&1
echo ====================================================== >> "%LOG_FILE%" 2>&1

:: 5. 错误提醒
if %EXIT_CODE% neq 0 (
    echo [%time%] [ERROR] 脚本运行失败！退出码：%EXIT_CODE%
    pause
    exit /b %EXIT_CODE%
)

:: 正式运行时取消下面的注释来自动关闭窗口
:: pause