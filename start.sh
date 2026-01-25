#!/bin/bash

PROJECT_ROOT="/Users/tk/Desktop/notebook-storyboard"

trap 'kill 0' SIGINT

echo "启动后端服务..."
cd "$PROJECT_ROOT/backend"
uvicorn app.ag_ui.server:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!

echo "启动前端服务..."
cd "$PROJECT_ROOT/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "服务已启动:"
echo "- 后端 PID: $BACKEND_PID"
echo "- 前端 PID: $FRONTEND_PID"
echo "- 访问地址: http://localhost:3847/storybook"
echo ""
echo "按 Ctrl+C 停止所有服务"

wait
