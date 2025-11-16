#!/bin/bash
# Quick start script for Voicebot Backend

echo "🚀 Setting up Voicebot Backend..."
echo ""

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your OpenAI API key!"
    echo "   OPENAI_API_KEY=sk-your-actual-key-here"
    echo ""
fi

# Create temp directories
mkdir -p temp_audio logs

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your OPENAI_API_KEY"
echo "2. Run: source venv/bin/activate (if not already activated)"
echo "3. Run: uvicorn app.main:app --reload"
echo "4. Open: http://localhost:8000/docs"
echo ""
echo "🎉 Happy coding!"
