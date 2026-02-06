@echo off
chcp 65001 >nul
echo ========================================
echo   安装 python-pptx 依赖
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python
    pause
    exit /b 1
)

echo 📦 正在安装 python-pptx...
echo.

python -m pip install python-pptx

if errorlevel 1 (
    echo.
    echo ⚠️  安装可能有问题，请手动运行:
    echo    pip install python-pptx
    pause
    exit /b 1
)

echo.
echo ✅ python-pptx 安装完成!
echo.
echo 💡 现在可以重启 File Converter 服务使用 PDF 转 PPT 功能
echo.

pause
