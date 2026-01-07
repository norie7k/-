@echo off
chcp 65001 >nul
echo ========================================
echo 每日输出格式转换工具
echo ========================================
echo.

cd /d "E:\项目\玩家社群分析智能体"

echo 使用方法：
echo   1. 将你的 JSON 数据保存到一个文本文件（如 daily_output.txt）
echo   2. 运行此脚本，按提示输入信息
echo.

set /p INPUT_FILE="请输入输入文件路径（如 daily_output.txt 或 预计算方案/daily_output.txt，或直接回车使用默认值）: "
if "%INPUT_FILE%"=="" set INPUT_FILE="预计算方案/daily_output.txt"

set /p GROUP_ID="请输入群组ID (1 或 2，或直接回车使用默认值 1): "
if "%GROUP_ID%"=="" set GROUP_ID=1

set /p DATE="请输入日期 (YYYY-MM-DD，如 2026-01-01，或直接回车自动提取): "

if "%DATE%"=="" (
    python "预计算方案/convert_daily_output.py" "%INPUT_FILE%" --group %GROUP_ID%
) else (
    python "预计算方案/convert_daily_output.py" "%INPUT_FILE%" --group %GROUP_ID% --date %DATE%
)

echo.
pause
