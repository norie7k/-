@echo off
chcp 65001 >nul
echo ========================================
echo 快速转换（使用默认值）
echo ========================================
echo.

cd /d "E:\项目\玩家社群分析智能体"

REM 默认值设置
set INPUT_FILE=预计算方案/daily_output.txt
set GROUP_ID=1
set DATE=2026-01-01

echo 使用默认设置：
echo   输入文件: %INPUT_FILE%
echo   群组ID: %GROUP_ID%
echo   日期: %DATE%
echo.
echo 如果要修改，请编辑此批处理文件或使用"转换每日数据.bat"
echo.

python "预计算方案/convert_daily_output.py" "%INPUT_FILE%" --group %GROUP_ID% --date %DATE%

echo.
echo 按任意键查看结果文件夹...
pause >nul
if exist "预计算方案\results\group%GROUP_ID%" (
    explorer "预计算方案\results\group%GROUP_ID%"
) else (
    echo 结果文件夹不存在
)

