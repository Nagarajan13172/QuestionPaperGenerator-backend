#!/bin/bash

# Quick start script for Question Paper Generator Backend

echo "🚀 Question Paper Generator - Quick Start"
echo "========================================="
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your GEMINI_API_KEY"
    echo "   Get your API key from: https://makersuite.google.com/app/apikey"
    echo ""
    read -p "Press Enter once you've added your API key..."
fi

# Start the server
echo ""
echo "🎯 Starting FastAPI server..."
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/api/docs"
echo ""
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
