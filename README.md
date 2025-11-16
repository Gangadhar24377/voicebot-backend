# 🎙️ Voicebot Backend - AI Interview Assistant

AI-powered voice and text chatbot representing **Gangadhar K** for the 100x AI Agent Team interview process.

## 🚀 Features

- **Text Chat**: Real-time text-based conversations with AI
- **Voice Chat**: Audio upload → transcription → AI response → TTS
- **Session Management**: Conversation history with automatic cleanup
- **Audio Caching**: Efficient TTS caching to reduce API calls
- **Health Monitoring**: Service status and connectivity checks
- **Production Ready**: Proper error handling, logging, and security

## 🏗️ Architecture

```
├── FastAPI Backend (Python)
│   ├── OpenAI GPT-4o-mini (Chat)
│   ├── OpenAI Whisper (Speech-to-Text)
│   ├── OpenAI TTS (Text-to-Speech)
│   └── In-memory Session Management
```

## 📋 Prerequisites

- Python 3.9+
- OpenAI API Key
- pip or poetry

## ⚙️ Installation

### 1. Clone & Setup

```bash
cd voicebot-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# IMPORTANT: Replace 'your_openai_api_key_here' with your actual key
```

**Required `.env` configuration:**
```env
OPENAI_API_KEY=sk-your-actual-key-here
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 3. Run Development Server

```bash
# Run with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or run directly
python -m app.main
```

Server will start at: **http://localhost:8000**

API Documentation: **http://localhost:8000/docs**

## 🔌 API Endpoints

### Health Check
```bash
GET /api/health
```

### Text Chat
```bash
POST /api/chat
Content-Type: application/json

{
  "message": "What should we know about your life story?",
  "session_id": "optional-uuid"
}
```

### Voice Chat
```bash
POST /api/voice-chat
Content-Type: multipart/form-data

audio: <audio-file>
session_id: optional-uuid
```

### Text-to-Speech
```bash
POST /api/tts
Content-Type: application/json

{
  "text": "Hello, I'm Gangadhar!",
  "voice": "alloy"
}
```

### Get Audio File
```bash
GET /api/audio/{audio_id}
```

## 🧪 Testing

```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Test chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is your superpower?"}'

# Test with audio (replace with actual audio file)
curl -X POST http://localhost:8000/api/voice-chat \
  -F "audio=@test.wav"
```

## 🌐 Deployment

### Option 1: Render.com (Recommended)

1. **Create account** at [render.com](https://render.com)

2. **New Web Service** → Connect your GitHub repo

3. **Configure:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Environment Variables:**
   ```
   OPENAI_API_KEY=sk-your-key
   ENVIRONMENT=production
   DEBUG=False
   CORS_ORIGINS=https://your-frontend.vercel.app
   ```

5. **Deploy!** ✨

### Option 2: Railway.app

1. **Create account** at [railway.app](https://railway.app)

2. **New Project** → Deploy from GitHub

3. **Add Environment Variables**

4. Railway auto-detects Python and deploys!

### Option 3: Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login and launch
flyctl auth login
flyctl launch

# Set secrets
flyctl secrets set OPENAI_API_KEY=sk-your-key

# Deploy
flyctl deploy
```

### Option 4: Docker

```bash
# Build image
docker build -t voicebot-backend .

# Run container
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=sk-your-key \
  voicebot-backend
```

## 📁 Project Structure

```
voicebot-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── routes/
│   │   ├── chat.py            # Text chat endpoints
│   │   ├── voice.py           # Voice endpoints
│   │   └── health.py          # Health check
│   ├── services/
│   │   ├── openai_service.py  # OpenAI API wrapper
│   │   ├── conversation_manager.py  # Session management
│   │   └── tts_service.py     # Text-to-speech service
│   ├── models/
│   │   └── schemas.py         # Pydantic models
│   ├── prompts/
│   │   └── system_prompt.py   # AI personality/context
│   └── utils/
│       └── logger.py          # Logging utilities
├── requirements.txt
├── .env
├── .env.example
├── Dockerfile
└── README.md
```

## 🔧 Configuration

All configuration is via environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | *required* |
| `OPENAI_MODEL` | GPT model to use | `gpt-4o-mini` |
| `OPENAI_TTS_VOICE` | TTS voice | `alloy` |
| `CORS_ORIGINS` | Allowed origins (comma-separated) | `http://localhost:3000` |
| `MAX_CONVERSATION_LENGTH` | Max messages to keep | `20` |
| `SESSION_TIMEOUT_SECONDS` | Session expiry | `3600` |
| `MAX_AUDIO_FILE_SIZE_MB` | Max audio upload size | `25` |

## 🐛 Troubleshooting

### OpenAI API Error
```bash
# Check API key is set
echo $OPENAI_API_KEY

# Test connectivity
curl -X GET http://localhost:8000/api/health
```

### CORS Issues
- Add your frontend URL to `CORS_ORIGINS` in `.env`
- Format: `http://localhost:3000,https://yourdomain.com`

### Port Already in Use
```bash
# Change port in .env
PORT=8001

# Or kill existing process
# Windows:
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Mac/Linux:
lsof -ti:8000 | xargs kill -9
```

## 📊 Monitoring

### View Logs
```bash
# Development
# Logs automatically print to console

# Production (if file logging enabled)
tail -f logs/app_*.log
```

### Check Stats
```bash
curl http://localhost:8000/api/stats
```

## 🔐 Security Considerations

- ✅ API keys stored in environment variables (never in code)
- ✅ CORS properly configured
- ✅ Request validation with Pydantic
- ✅ File size limits enforced
- ✅ Session timeouts implemented
- ✅ Error messages sanitized in production

## 💡 Customization

### Update System Prompt
Edit `app/prompts/system_prompt.py` to change AI personality and knowledge.

### Adjust Voice
Change TTS voice in `.env`:
```env
OPENAI_TTS_VOICE=alloy  # or echo, fable, onyx, nova, shimmer
```

### Modify Session Timeout
```env
SESSION_TIMEOUT_SECONDS=7200  # 2 hours
```

## 📝 API Cost Estimation

Based on typical usage:

| Operation | Cost per Unit | Example |
|-----------|---------------|---------|
| Chat (GPT-4o-mini) | ~$0.15/1M input tokens | $0.0001 per message |
| TTS | $15/1M characters | $0.015 per 1000 chars |
| Whisper | $0.006/minute | $0.006 per minute |

**Estimated cost per full interview:** ~$0.10-0.25

## 🤝 Contributing

This is a job application project, but suggestions welcome!

## 📧 Contact

**Gangadhar K**
- Email: gangadharkambhamettu@gmail.com
- LinkedIn: [in/gangadhar-kambhamettu-086a48227](https://linkedin.com/in/gangadhar-kambhamettu-086a48227)
- GitHub: [Gangadhar24377](https://github.com/Gangadhar24377)
