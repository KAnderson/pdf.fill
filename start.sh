#!/bin/bash

# PDF Form Filler - Web UI Launcher
# Simple script to start the web interface

echo "🚀 Starting PDF Form Filler Web UI..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if Flask is installed
if ! python -c "import flask" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

echo "✅ Dependencies ready"
echo ""
echo "🌐 Starting web server..."
echo "   URL: http://localhost:5000"
echo ""
echo "   Press Ctrl+C to stop"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start Flask app
python app.py
