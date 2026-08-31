#!/bin/bash
# Nexus AI Safety Research Platform - Startup Script

set -e

echo "🚀 Starting Nexus AI Safety Research Platform..."

# Check if .env exists
if [ ! -f backend/.env ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp backend/.env.example backend/.env
    echo "📝 Please edit backend/.env and add your API keys"
    exit 1
fi

# Load environment
export $(cat backend/.env | grep -v '^#' | xargs)

# Check Ollama
echo "🔍 Checking Ollama..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama not running. Starting Ollama..."
    ollama serve &
    sleep 3
fi

# Pull Gemma model if not present
echo "📦 Checking for Gemma model..."
if ! ollama list | grep -q "gemma2:9b-instruct-q4_K_M"; then
    echo "📥 Pulling Gemma 2 9B model (this may take a while)..."
    ollama pull gemma2:9b-instruct-q4_K_M
fi

# Check ChromaDB
echo "🔍 Checking ChromaDB..."
if ! curl -s http://localhost:8000/api/v1/heartbeat > /dev/null 2>&1; then
    echo "⚠️  ChromaDB not running. Starting ChromaDB..."
    docker run -d --name chromadb -p 8000:8000 chromadb/chroma:latest &
    sleep 3
fi

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Start backend
echo "🚀 Starting backend server..."
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend
sleep 3

# Start frontend
echo "🚀 Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Nexus is running!"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Trap SIGINT
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '👋 Shutting down...'; exit 0" INT

# Wait
wait