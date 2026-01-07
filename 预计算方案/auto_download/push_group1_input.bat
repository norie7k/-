@echo off
chcp 65001 >nul
cd /d "E:\项目\玩家社群分析智能体"
echo ============================================================
echo 推送 group1_input.json 到 GitHub
echo ============================================================
echo.

echo [1/3] 添加文件到 Git...
git add "预计算方案\results\group1_input.json"
if %errorlevel% neq 0 (
    echo ❌ git add 失败
    pause
    exit /b 1
)
echo ✅ git add 完成
echo.

echo [2/3] 提交更改...
git commit -m "[更新] 添加 group1 2025-12-31 的分析结果到 group1_input.json"
if %errorlevel% neq 0 (
    echo ⚠️  commit 可能没有新更改，继续推送...
)
echo ✅ git commit 完成
echo.

echo [3/3] 推送到 GitHub...
git push
if %errorlevel% neq 0 (
    echo ❌ git push 失败
    pause
    exit /b 1
)
echo ✅ git push 完成！
echo.
echo ============================================================
echo 🎉 完成！group1_input.json 已推送到 GitHub
echo ============================================================
pause


