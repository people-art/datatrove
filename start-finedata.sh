#!/bin/bash

# FineData - 启动脚本
# 用于快速启动前端和后端服务

set -e

echo "🚀 Starting FineData..."

# 检查依赖
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed. Aborting." >&2; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed. Aborting." >&2; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "❌ npm is required but not installed. Aborting." >&2; exit 1; }

# 设置后端
echo "📦 Setting up backend..."
cd api

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "🔧 Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit api/.env with your configuration before running in production!"
fi

# 设置前端
echo "🎨 Setting up frontend..."
cd ../web

if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# 检查前端环境变量
if [ ! -f ".env.local" ]; then
    echo "⚙️  Creating .env.local file..."
    cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
EOF
fi

# 启动服务
echo "🌟 Starting services..."

# 启动后端（后台）
echo "🔧 Starting backend server..."
cd ../api
source venv/bin/activate
python main.py &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动前端（后台）
echo "🎨 Starting frontend server..."
cd ../web
npm run dev &
FRONTEND_PID=$!

# 等待前端启动
sleep 5

echo ""
echo "✅ FineData is running!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "📝 To stop services, press Ctrl+C or run: kill $BACKEND_PID $FRONTEND_PID"
echo ""

# 等待用户中断
trap "echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
