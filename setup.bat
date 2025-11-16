@echo off
REM Quick start script for Voicebot Backend (Windows)

echo 🚀 Setting up Voicebot Backend...
echo.

REM Check Python version
python --version
echo.

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Check if .env exists
if not exist .env (
    echo 📝 Creating .env file...
    copy .env.example .env
    echo.
    echo ⚠️  IMPORTANT: Edit .env file and add your OpenAI API key!
    echo    OPENAI_API_KEY=sk-your-actual-key-here
    echo.
)

REM Create temp directories
if not exist temp_audio mkdir temp_audio
if not exist logs mkdir logs

echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Edit .env and add your OPENAI_API_KEY
echo 2. Run: venv\Scripts\activate.bat (if not already activated)
echo 3. Run: uvicorn app.main:app --reload
echo 4. Open: http://localhost:8000/docs
echo.
echo 🎉 Happy coding!
pause
