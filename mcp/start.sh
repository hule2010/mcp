#!/bin/bash

# MCP 工作流系统启动脚本

echo "🚀 MCP 自然语言工作流系统"
echo "=========================="

# 检查 Python 版本
python_version=$(python3 --version 2>&1)
if [[ $? -ne 0 ]]; then
    echo "❌ 错误: 未找到 Python 3"
    echo "请安装 Python 3.8 或更高版本"
    exit 1
fi
echo "✅ Python 版本: $python_version"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装/更新依赖
echo "📥 检查并安装依赖..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# 检查环境变量文件
if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        echo "⚠️  未找到 .env 文件"
        echo "📝 从 env.example 创建 .env 文件..."
        cp env.example .env
        echo "请编辑 .env 文件，填入您的 API 密钥和配置"
        echo "然后重新运行此脚本"
        exit 1
    fi
fi

# 检查必要的环境变量
source .env
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "❌ 错误: DEEPSEEK_API_KEY 未设置"
    echo "请在 .env 文件中设置 DEEPSEEK_API_KEY"
    exit 1
fi

echo "✅ 环境配置完成"

# 启动服务
echo ""
echo "🌐 启动 FastAPI 服务..."
echo "服务地址: http://localhost:8000"
echo "API 文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo "=========================="

# 启动 uvicorn
uvicorn app:app --reload --host 0.0.0.0 --port 8000 