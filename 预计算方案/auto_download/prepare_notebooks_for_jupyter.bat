@echo off
chcp 65001 >nul
cd /d "%~dp0\..\.."
python "预计算方案\auto_download\prepare_notebooks_for_jupyter.py" %*
pause

