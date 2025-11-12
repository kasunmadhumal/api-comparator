#!/bin/bash

# API Comparator Startup Script

echo "🚀 Starting API Comparator..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install/update requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet

# Create data directory if it doesn't exist
mkdir -p data

# Start Streamlit
echo "✅ Launching application..."
echo "🌐 Access the app at: http://localhost:8501"
echo "Press Ctrl+C to stop the application"
echo ""

streamlit run app.py
