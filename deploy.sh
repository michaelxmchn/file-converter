#!/bin/bash

# File Converter 一键部署脚本
# 用法: bash deploy.sh

set -e

echo "========================================"
echo "  File Converter - 自动化部署脚本"
echo "========================================"

# 检查 Python 版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3，请先安装 Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "🐍 Python 版本: $PYTHON_VERSION"

# 创建虚拟环境
echo "\n📦 创建 Python 虚拟环境..."
if [ -d "venv" ]; then
    echo "⚠️  虚拟环境已存在，跳过创建"
else
    python3 -m venv venv
    echo "✓ 虚拟环境创建成功"
fi

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
echo "\n⬆️  升级 pip..."
pip install --upgrade pip -q

# 安装依赖
echo "\n📥 安装 Python 依赖..."
pip install -r requirements.txt -q

# 创建必要目录
echo "\n📂 创建目录结构..."
python3 -c "
from pathlib import Path
for dir in ['input', 'output', 'logs']:
    Path(dir).mkdir(exist_ok=True)
print('✓ 目录创建完成')
"

# 测试运行
echo "\n🧪 测试运行..."
python3 main.py

echo "\n========================================"
echo "✅ 部署完成!"
echo "========================================"
echo "\n下一步:"
echo "  1. 激活虚拟环境: source venv/bin/activate"
echo "  2. 运行程序: python3 main.py"
echo "  3. 或启动服务: uvicorn main:app --host 0.0.0.0 --port 8000"
