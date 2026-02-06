@echo off
chcp 65001 >nul
echo ========================================
echo   文件转换器 - 启动脚本 (Windows)
echo ========================================
echo.

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 设置 Python 路径
set PYTHON_PATH=%~dp0python\Python310\python.exe

REM 检查 Python 是否存在
if not exist "%PYTHON_PATH%" (
    echo ❌ 错误: 未找到 Python，请检查 python 目录
    pause
    exit /b 1
)

echo 🐍 使用 Python: %PYTHON_PATH%

REM 检查依赖
echo.
echo 📦 检查依赖...
%PYTHON_PATH% -c "import fastapi, uvicorn, pdfplumber, python_docx" 2>nul
if errorlevel 1 (
    echo ⚠️  依赖缺失，正在安装...
    %PYTHON_PATH% -m pip install fastapi uvicorn python-multipart aiofiles pdfplumber python-docx loguru python-dotenv
    echo ✅ 依赖安装完成
) else (
    echo ✅ 依赖检查通过
)

REM 创建必要目录
echo.
echo 📂 创建目录...
if not exist input mkdir input
if not exist output mkdir output
if not exist logs mkdir logs
echo ✅ 目录就绪

REM 启动服务
echo.
echo 🚀 启动服务...
echo ========================================
echo.
echo 📍 本机访问: http://localhost:8000
echo 🌐 局域网访问: http://{IP}:8000
echo.
echo 按 Ctrl+C 停止服务
echo.
echo ========================================

%PYTHON_PATH% main.py

pause
