@echo off
chcp 65001 >nul
echo ========================================
echo   安装所有依赖
echo ========================================
echo.

REM 检查 Python
python --version
echo.

echo 📦 正在安装依赖...
echo.

REM 安装 requirements.txt 中的所有依赖
pip install -r requirements.txt

echo.
echo ✅ 依赖安装完成!
echo.

pause
