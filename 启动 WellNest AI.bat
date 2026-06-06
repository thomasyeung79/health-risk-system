@echo off
title WellNest AI - 健康管理平台
cd /d "%~dp0"
echo.
echo  ========================================
echo    WellNest AI - 正在启动...
echo  ========================================
echo.
echo  应用将在浏览器中自动打开
echo  如果未自动打开，请访问：
echo  http://localhost:8501
echo.
echo  按 Ctrl+C 关闭应用
echo.
start http://localhost:8501
python -m streamlit run web_v1.py --server.port 8501 --browser.gatherUsageStats false
pause
