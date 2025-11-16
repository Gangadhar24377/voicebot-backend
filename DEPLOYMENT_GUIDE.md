# 🚀 Deployment Guide - Voicebot Backend

Complete guide to deploy your backend for the 100x interview assessment.

## ⚡ Quick Start (Local Development)

### Windows:
```bash
# 1. Navigate to project
cd voicebot-backend

# 2. Run setup script
setup.bat

# 3. Edit .env file with your OpenAI key
# Open .env in notepad and replace: OPENAI_API_KEY=sk-your-key-here

# 4. Start server
venv\Scripts\activate
uvicorn app.main:app --reload
```

### Mac/Linux:
```bash
# 1. Navigate to project
cd voicebot-backend

# 2. Run setup script
chmod +x setup.sh
./setup.sh

# 3. Edit .env file with your OpenAI key
nano .env  # or use your preferred editor

# 4. Start server
source venv/bin/activate
uvicorn app.main:app --reload
```

**Server will run at:** http://localhost:8000  
**API Docs:** http://localhost:8000/docs

---

## 🌐 Production Deployment

For the 100x assessment, you need to deploy this so non-technical users can access it. Here are the **3 best options**:

### Option 1: Render.com ⭐ (RECOMMENDED - Easiest)

**Why:** Free tier, automatic SSL, easiest setup, perfect for demos.

#### Steps:

1. **Push code to GitHub**
   ```bash
   cd voicebot-backend
   git init
   git add .
   git commit -m "Initial commit - Voicebot backend"
   
   # Create repo on GitHub, then:
   git remote add origin https://github.com/YOUR_USERNAME/voicebot-backend.git
   git push -u origin main
   ```

2. **Deploy on Render**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Render auto-detects settings from `render.yaml`!

3. **Add Environment Variable**
   - In Render dashboard → Environment
   - Add: `OPENAI_API_KEY` = `sk-your-key`
   - Add: `CORS_ORIGINS` = `https://your-frontend-url.vercel.app`

4. **Deploy**
   - Click "Create Web Service"
   - Wait 3-5 minutes for build
   - Your backend is live! 🎉

5. **Get Your URL**
   - Copy the URL: `https://voicebot-backend-xxxx.onrender.com`
   - Test: `https://your-url.onrender.com/api/health`

**⚠️ Free tier sleeps after 15 min inactivity (first request takes ~30s to wake up)**

---

### Option 2: Railway.app (Fast & Modern)

**Why:** Generous free tier, great DX, fast deployment.

#### Steps:

1. **Push to GitHub** (same as Option 1)

2. **Deploy on Railway**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repo

3. **Configure**
   - Railway auto-detects Python
   - Add environment variables:
     ```
     OPENAI_API_KEY=sk-your-key
     CORS_ORIGINS=https://your-frontend.vercel.app
     ```

4. **Generate Domain**
   - Settings → Generate Domain
   - Get URL: `https://voicebot-backend-production.up.railway.app`

5. **Deploy automatically!** ✨

**💡 Tip:** Railway gives $5/month free credit (enough for demos)

---

### Option 3: Fly.io (Most Professional)

**Why:** Best for production-grade deployments, global CDN.

#### Steps:

1. **Install Fly CLI**
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   
   # Mac/Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login & Deploy**
   ```bash
   cd voicebot-backend
   
   # Login
   flyctl auth login
   
   # Create app
   flyctl launch
   # Answer prompts:
   # - App name: voicebot-backend-yourname
   # - Region: Choose closest
   # - PostgreSQL: No
   # - Redis: No
   ```

3. **Set Secrets**
   ```bash
   flyctl secrets set OPENAI_API_KEY=sk-your-key
   flyctl secrets set CORS_ORIGINS=https://your-frontend.vercel.app
   ```

4. **Deploy**
   ```bash
   flyctl deploy
   ```

5. **Get URL**
   ```bash
   flyctl info
   # URL: https://voicebot-backend-yourname.fly.dev
   ```

---

## 🔗 Connecting Frontend to Backend

Once deployed, update your frontend to use the backend URL:

```javascript
// In your frontend config
const API_BASE_URL = "https://your-backend-url.onrender.com";

// API calls
fetch(`${API_BASE_URL}/api/chat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: "Hello!" })
});
```

**Important:** Update `CORS_ORIGINS` in backend `.env` with your frontend URL!

---

## ✅ Pre-Submission Checklist

Before submitting to 100x:

- [ ] Backend deployed and accessible via URL
- [ ] `/api/health` endpoint returns `{"status": "healthy"}`
- [ ] Test chat endpoint works
- [ ] Test voice endpoint works (if using)
- [ ] CORS configured for frontend domain
- [ ] No API key exposed in frontend code
- [ ] README includes backend URL
- [ ] Test on different devices (mobile, desktop)

---

## 🧪 Testing Your Deployment

### 1. Health Check
```bash
curl https://your-backend-url.com/api/health
```

Expected:
```json
{
  "status": "healthy",
  "timestamp": "2024-11-17T...",
  "openai_connected": true,
  "version": "1.0.0"
}
```

### 2. Chat Test
```bash
curl -X POST https://your-backend-url.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is your superpower?"}'
```

### 3. Test in Browser
Visit: `https://your-backend-url.com/docs`

Try the interactive API documentation!

---

## 🐛 Troubleshooting

### "OpenAI API Error"
- **Check:** Is `OPENAI_API_KEY` set correctly in deployment environment?
- **Test:** `curl https://api.openai.com/v1/models -H "Authorization: Bearer YOUR_KEY"`

### "CORS Error"
- **Fix:** Add your frontend URL to `CORS_ORIGINS` environment variable
- **Format:** `https://frontend.vercel.app,https://frontend-staging.vercel.app`

### "Service Unavailable"
- **Render:** Check if service is sleeping (free tier)
- **Fix:** Use a cron job to ping every 10 minutes
- **Or:** Upgrade to paid tier ($7/month)

### "Build Failed"
- **Check:** All dependencies in `requirements.txt`
- **Fix:** Look at build logs for missing packages
- **Common:** May need to add `python-multipart`

---

## 💰 Cost Breakdown

### Deployment Costs (Monthly)

| Platform | Free Tier | Paid Tier |
|----------|-----------|-----------|
| **Render** | Free (sleeps after 15min) | $7/month |
| **Railway** | $5 credit/month | $5/month usage |
| **Fly.io** | 3 small VMs free | Pay-as-you-go |

### API Costs (OpenAI)

For typical interview demo:
- **GPT-4o-mini:** ~$0.15 per 1M tokens
- **Whisper:** $0.006 per minute
- **TTS:** $15 per 1M characters

**Estimated cost per demo:** $0.10 - $0.25  
**For 100 test interviews:** ~$10-25

---

## 🎯 Recommended Setup for 100x Assessment

### Best Configuration:

1. **Backend:** Render.com (free tier with render.yaml)
2. **Frontend:** Vercel (to be created next)
3. **Monitoring:** Render dashboard + OpenAI usage dashboard

### Environment Variables:
```env
OPENAI_API_KEY=sk-your-key
ENVIRONMENT=production
DEBUG=False
CORS_ORIGINS=https://your-frontend.vercel.app
OPENAI_MODEL=gpt-4o-mini
MAX_CONVERSATION_LENGTH=20
SESSION_TIMEOUT_SECONDS=3600
```

---

## 📊 Monitoring Your Deployment

### Check Logs

**Render:**
- Dashboard → Logs tab
- Real-time log streaming

**Railway:**
- Deployment → View Logs

**Fly.io:**
```bash
flyctl logs
```

### Monitor Usage

**OpenAI Dashboard:**
- [platform.openai.com/usage](https://platform.openai.com/usage)
- Track API costs and requests

### Custom Stats Endpoint
```bash
curl https://your-backend-url.com/api/stats
```

Returns:
```json
{
  "sessions": {
    "active_sessions": 5,
    "total_messages": 42
  },
  "storage": {
    "total_files": 12,
    "total_size_mb": 3.5
  }
}
```

---

## 🚨 Important Notes for Assessment

1. **No API Key in Frontend:** Always use backend to call OpenAI
2. **Test Everything:** Chat, voice, health checks
3. **Mobile-Friendly:** Test on mobile browsers
4. **Fast Response:** Keep backend warm or warn about cold starts
5. **Error Handling:** Graceful error messages for users

---

## 📞 Need Help?

**Common Issues:**
- [Render Docs](https://render.com/docs)
- [Railway Docs](https://docs.railway.app)
- [Fly.io Docs](https://fly.io/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com)

**For Assessment Questions:**
Contact 100x team at: bhumika@100x.inc

---

## 🎉 You're Ready!

Your backend is production-ready with:
- ✅ Proper API key management
- ✅ CORS configuration
- ✅ Error handling
- ✅ Session management
- ✅ Logging and monitoring
- ✅ Scalable architecture

**Next Step:** Build the frontend! 🚀

---

**Good luck with your 100x interview! 💪**
